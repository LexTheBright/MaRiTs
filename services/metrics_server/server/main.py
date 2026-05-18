"""Реализация сервера для приема метрик с сохранением в InfluxDB"""

from time import time 
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
    """
    Инициализация подключения к InfluxDB.

    Читает конфигурацию из переменных окружения:
    - INFLUX_URL: URL сервера InfluxDB
    - INFLUX_TOKEN: Токен доступа
    - INFLUX_ORG: Организация
    - INFLUX_BUCKET: Bucket для записи

    Если токен не установлен, работает в режиме "только память" (без сохранения).
    """
    global _influx_client, _influx_write_api, _influx_query_api, _influx_bucket, _influx_org
    
    url = os.getenv("INFLUX_URL", "http://localhost:8086")
    token = os.getenv("INFLUX_TOKEN", "MySuperSecretToken123==")
    org = os.getenv("INFLUX_ORG", "MaRiTs")
    bucket = os.getenv("INFLUX_BUCKET", "cpu-metrics")
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
    """
    Протокол сервера для приема и обработки метрик.

    Реализует простой текстовый протокол с командами:
    - put <metric> <value> <timestamp> - сохранить метрику
    - get <metric1> [metric2 ...] - получить значения метрик
    - list - получить список всех имен метрик

    Данные сохраняются в InfluxDB (если настроено) или возвращают ошибку.
    """

    def connection_made(self, transport):
        self.transport = transport
        peer = transport.get_extra_info("peername")
        # print(f"🔗 New connection from {peer}")

    def data_received(self, data):
        """
        Обработка поступивших данных.

        Парсит команду клиента и вызывает соответствующий обработчик.

        Args:
            data: Сырые данные от клиента (байты)
        """
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
        elif cmd == "list": 
            result = self._handle_list()
        else:
            result = "error\nunknown command\n\n"
        self.transport.write(result.encode("utf-8"))

    def _handle_get(self, chunks: List[str]) -> str:
        """
        Обработка команды get.

        Args:
            chunks: Разобранная команда (первый элемент - "get", остальные - имена метрик)

        Returns:
            Ответ сервера в формате "ok\\n<данные>\\n\\n" или "error\\n<описание>\\n\\n"
        """
        if len(chunks) < 2:
            return "error\nmissing key\n\n"
        
        requested_keys = chunks[1:]
        result_lines = []

        # print(f"DEBUG: Processing GET for keys: {requested_keys}") # Видно в Docker

        try:
            if _influx_query_api and _influx_bucket:
                
                if requested_keys == "*":
                    key_filter = ""
                else:
                    filters = " or ".join([f'r.metric_key == "{k}"' for k in requested_keys])
                    key_filter = f'|> filter(fn: (r) => {filters})'
                
                query = f'''
                    from(bucket: "{_influx_bucket}")

                    |> range(start: -1d)
                    |> filter(fn: (r) => r._measurement == "{METRICS_MEASUREMENT}")
                    {key_filter}
                    |> sort(columns: ["_time"])
                '''
                
                # print(f"DEBUG: Executing Flux: {query}")
                # t = time()
                tables = _influx_query_api.query(query, org=_influx_org)
                # print(f"✅ Query took {time() - t:.3f} seconds")

                count = 0
                for table in tables:
                    for record in table.records:
                        # Теперь get_value() сработает, так как мы не делали pivot
                        val = record.get_value()
                        # Извлекаем тег metric_key напрямую из записи
                        m_key = record.values.get("metric_key")
                        # Преобразуем время через ваш парсер
                        ts = _parse_influx_timestamp(str(record.get_time()))
                        
                        if val is not None and m_key:
                            result_lines.append(f"{m_key} {val} {ts}")
                            count += 1
                
                # print(f"DEBUG: Found {count} records in InfluxDB")
            else:
                print("ERROR: InfluxDB query API not initialized")
                return "error\ninternal error\n\n"
                
        except Exception as e:
            print(f"❌ Query error details: {type(e).__name__}: {e}")
            return f"error\ninternal error\n\n"

        # Формируем ответ
        response = "ok\n" + "\n".join(result_lines) + "\n\n"
        return response

   
    def _handle_put(self, chunks: List[str]) -> str:
        """
        Обработка команды put.

        Args:
            chunks: Разобранная команда ["put", metric, value, timestamp]

        Returns:
            Ответ сервера в формате "ok\\n\\n" или "error\\n<описание>\\n\\n"
        """   
        if len(chunks) < 4:
            return "error\nwrong number of arguments\n\n"
        
        key, val_str, ts_str = chunks[1], chunks[2], chunks[3]
        # print(f"DEBUG: PUT received - Key: {key}, Val: {val_str}, TS: {ts_str}")

        try:
            value = float(val_str)
            timestamp = int(ts_str)
            
            if _influx_write_api:
                point = (
                    Point(METRICS_MEASUREMENT)
                    .tag("metric_key", key)
                    .field("value", value)
                    .time(timestamp, WritePrecision.S)
                )
                _influx_write_api.write(bucket=_influx_bucket, record=point)
                # print(f"DEBUG: Successfully wrote {key} to InfluxDB")
                return "ok\n\n"
            else:
                print("ERROR: InfluxDB Write API is missing (check token/url)")
                return "error\ndatabase offline\n\n"

        except ValueError:
            print(f"ERROR: Bad data format in PUT: {chunks}")
            return "error\nvalue error\n\n"
        except Exception as e:
            print(f"❌ Write error: {e}")
            return "error\ninternal error\n\n"

    def _handle_list(self) -> str:
        """
        Возвращает список уникальных имен метрик (metric_key).

        Returns:
            Ответ сервера в формате "ok\\n<metric1>\\n<metric2>\\n...\\n\\n"
            или "error\\ndatabase offline\\n\\n"
        """
        try:
            if _influx_query_api and _influx_bucket:
                # Используем schema.tagValues для мгновенного получения имен из индексов
                query = f'''
                    import "influxdata/influxdb/schema"
                    schema.tagValues(
                        bucket: "{_influx_bucket}",
                        tag: "metric_key",
                        start: -1d
                    )
                '''
                tables = _influx_query_api.query(query, org=_influx_org)
                
                names = []
                for table in tables:
                    for record in table.records:
                        names.append(record.get_value())
                
                response = "ok\n" + "\n".join(sorted(names)) + "\n\n"
                return response
            else:
                return "error\ndatabase offline\n\n"
        except Exception as e:
            print(f"❌ List error: {e}")
            return "error\ninternal error\n\n"


async def main():
    """
    Точка входа сервера.

    Инициализирует подключение к InfluxDB и запускает asyncio-сервер
    на порту 8888 для обработки запросов клиентов.
    """
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