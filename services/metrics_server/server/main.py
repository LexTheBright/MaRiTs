"""Реализация сервера для приема метрик с сохранением в InfluxDB"""

import os
import asyncio
from asyncio import Protocol, get_event_loop
from typing import TYPE_CHECKING, Optional, List

from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
from influxdb_client.client.exceptions import InfluxDBError

if TYPE_CHECKING:
    from typing import Dict, List, Tuple

# Глобальный клиент (инициализируется при старте)
_influx_client: Optional[InfluxDBClient] = None
_influx_write_api = None
_influx_query_api = None
_influx_bucket: Optional[str] = None
_influx_org: Optional[str] = None

# Название measurement в InfluxDB (все метрики пишем в одну таблицу)
METRICS_MEASUREMENT = "custom_metrics"


def init_influxdb():
    """Инициализация подключения к InfluxDB"""
    global _influx_client, _influx_write_api, _influx_query_api, _influx_bucket, _influx_org
    
    url = os.getenv("INFLUX_URL", "http://localhost:8086")
    token = os.getenv("INFLUX_TOKEN")
    org = os.getenv("INFLUX_ORG", "my-org")
    bucket = os.getenv("INFLUX_BUCKET", "metrics-bucket")
    
    if not token:
        print("⚠️  INFLUX_TOKEN not set, running in memory-only mode")
        return
    
    try:
        _influx_client = InfluxDBClient(url=url, token=token, org=org)
        _influx_write_api = _influx_client.write_api(write_options=SYNCHRONOUS)
        _influx_query_api = _influx_client.query_api()
        _influx_bucket = bucket
        _influx_org = org
        print(f"✅ Connected to InfluxDB: {url} (bucket: {bucket})")
    except Exception as e:
        print(f"❌ Failed to connect to InfluxDB: {e}")


def shutdown_influxdb():
    """Закрытие соединения при остановке сервера"""
    global _influx_client
    if _influx_client:
        _influx_client.close()
        print("🔌 InfluxDB connection closed")


def _parse_influx_timestamp(ts: str) -> int:
    """Конвертация строки времени из InfluxDB в unix timestamp"""
    # InfluxDB возвращает время в формате "2024-01-01T12:00:00Z"
    # или в наносекундах как число — обрабатываем оба варианта
    try:
        # Если это число (наносекунды)
        return int(float(ts) / 1_000_000_000)
    except ValueError:
        # Если это строка даты — парсим (упрощённо)
        from datetime import datetime
        try:
            dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
            return int(dt.timestamp())
        except:
            return 0


class ClientServerProtocol(Protocol):
    """Реализация протокола с сохранением в InfluxDB"""

    def connection_made(self, transport):
        self.transport = transport
        peer = transport.get_extra_info("peername")
        print(f"🔗 New connection from {peer}")

    def data_received(self, data):
        """Обработка поступивших данных"""
        result: str = "error\nwrong command\n\n"
        command: str = data.decode("utf-8").strip("\r\n")
        chunks: List[str] = command.split(" ")

        if not chunks:
            self.transport.write(result.encode("utf-8"))
            return

        cmd = chunks[0].lower()

        if cmd == "get":
            result = self._handle_get(chunks)
        elif cmd == "put":
            result = self._handle_put(chunks)
        else:
            result = "error\nunknown command\n\n"

        self.transport.write(result.encode("utf-8"))

    def _handle_get(self, chunks: List[str]) -> str:
        """Обработка команды get <key> или get *"""
        if len(chunks) < 2:
            return "error\nmissing key\n\n"
        
        key = chunks[1]
        result_lines = []

        try:
            if _influx_query_api and _influx_bucket:
                # Формируем Flux-запрос
                if key == "*":
                    # Все метрики
                    query = f'''
                        from(bucket: "{_influx_bucket}")
                        |> range(start: -30d)
                        |> filter(fn: (r) => r._measurement == "{METRICS_MEASUREMENT}")
                        |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
                        |> sort(columns: ["_time"])
                    '''
                else:
                    # Конкретный ключ → фильтр по тегу 'metric_key'
                    query = f'''
                        from(bucket: "{_influx_bucket}")
                        |> range(start: -30d)
                        |> filter(fn: (r) => r._measurement == "{METRICS_MEASUREMENT}")
                        |> filter(fn: (r) => r.metric_key == "{key}")
                        |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
                        |> sort(columns: ["_time"])
                    '''
                
                tables = _influx_query_api.query(query, org=_influx_org)
                
                for table in tables:
                    for record in table.records:
                        # Извлекаем значение и время
                        value = record.get_value()
                        ts = _parse_influx_timestamp(str(record.get_time()))
                        metric_key = record.values.get("metric_key", key)
                        if value is not None:
                            result_lines.append(f"{metric_key} {value} {ts}")
            else:
                # Fallback: если InfluxDB не подключен — возвращаем пусто
                pass
                
        except InfluxDBError as e:
            print(f"❌ InfluxDB query error: {e}")
            return f"error\ndatabase error\n\n"
        except Exception as e:
            print(f"❌ Query error: {e}")
            return f"error\ninternal error\n\n"

        # Формируем ответ в формате протокола
        result = "ok\n"
        for line in result_lines:
            result += f"{line}\n"
        result += "\n"
        return result

    def _handle_put(self, chunks: List[str]) -> str:
        """Обработка команды put <key> <value> <timestamp>"""
        if len(chunks) < 4:
            return "error\nwrong number of arguments\n\n"
        
        key = chunks[1]
        if key == "*":
            return "error\nkey cannot contain *\n\n"

        try:
            value: float = float(chunks[2])
            timestamp: int = int(chunks[3])
        except ValueError:
            return "error\nvalue error\n\n"

        # Пишем в InfluxDB, если клиент инициализирован
        if _influx_write_api and _influx_bucket:
            try:
                point = (
                    Point(METRICS_MEASUREMENT)
                    .tag("metric_key", key)          # ключ как тег — удобно для фильтрации
                    .field("value", value)            # значение как поле
                    .time(timestamp, WritePrecision.S) # время в секундах
                )
                _influx_write_api.write(bucket=_influx_bucket, record=point)
            except InfluxDBError as e:
                print(f"❌ InfluxDB write error: {e}")
                return "error\ndatabase write error\n\n"
            except Exception as e:
                print(f"❌ Write error: {e}")
                return "error\ninternal error\n\n"
        
        # Всегда возвращаем ok, даже если InfluxDB не подключен (fallback-режим)
        return "ok\n\n"


async def main():
    """Точка входа сервера"""
    # Инициализация InfluxDB
    init_influxdb()
    
    # Запуск asyncio-сервера
    loop = get_event_loop()
    server = await loop.create_server(
        lambda: ClientServerProtocol(),
        host="0.0.0.0",  # ← важно: слушаем все интерфейсы для Docker
        port=8888
    )
    
    print(f"🚀 Metrics server started on port 8888")
    
    try:
        await server.serve_forever()
    except asyncio.CancelledError:
        print("🛑 Server shutting down...")
        shutdown_influxdb()
        server.close()
        await server.wait_closed()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Stopped by user")
        shutdown_influxdb()