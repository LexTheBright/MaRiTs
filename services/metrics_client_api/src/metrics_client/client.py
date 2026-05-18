"""Реализация клиента для сервера метрик"""

import socket
from time import time
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Dict, List, Optional, Tuple, Union


class ClientError(Exception):
    """Общий класс исключений клиента"""

    ...


class ClientSocketError(ClientError):
    """Исключение, выбрасываемое клиентом при сетевой ошибке"""

    ...


class ClientProtocolError(ClientError):
    """Исключение, выбрасываемое клиентом при ошибке протокола"""

    ...


class Client:
    """
    Клиент для сервера метрик.

    Реализует простой текстовый протокол для отправки и получения метрик.
    Поддерживает пакетную отправку метрик и получение по имени.

    Attributes:
        connection: Кортеж (host, port) для подключения
        timeout: Таймаут подключения в секундах
    """

    def __init__(
        self, host: "str", port: "int", timeout: "Optional[int]" = None
    ):
        """Конструктор класса"""

        self.connection: "Tuple[str,int]" = (host, port)
        self.timeout: "Optional[int]" = timeout

    def send(self, cmd: "str") -> "str":
        """Отправка команд серверу"""
        data: "bytes" = b""

        try:
            with socket.create_connection(
                self.connection, self.timeout
            ) as sock:
                sock.sendall(cmd.encode("utf8"))

                while not data.endswith(b"\n\n"):
                    data += sock.recv(1024)

        except socket.error as err:
            raise ClientSocketError("error create connection", err) from err

        status, payload = data.decode("utf-8").split("\n", 1)
        payload: "str" = payload.strip()

        if status == "error":
            raise ClientProtocolError(payload)

        return payload

    def put(
        self, metric: "str", value: "float", timestamp: "Optional[int]" = None
    ) -> "None":
        """Метод отправки данных"""

        self.send(
            f"put {metric} {value} {timestamp if timestamp else int(time())}\n"
        )

    # def get(self, metric: "str") -> "Dict[str,List[Tuple[int,float]]]":
    #     """Метод получения данных"""

    #     result: "Dict[str,List[Tuple[int,float]]]" = {}
    
    #     for line in self.send(f"get {metric}\n").splitlines():
    #         try:
    #             _metric, value, timestamp = line.split()

    #             if not _metric in result:
    #                 result[_metric] = []

    #             result[_metric].append((int(timestamp), float(value)))

    #         except ValueError as error:
    #             raise ClientProtocolError(line) from error

    #     for item in result.items():
    #         item[1].sort(key=lambda stamp: stamp[0])

    #     return result

    def get(self, metric: "Union[str, list]", chunk_size: int = 50) -> "Dict[str, List[Tuple[int, float]]]":
        """
        Получение данных метрик с сервера.

        Поддерживает получение как одной метрики, так и списка метрик.
        Для больших списков используется пакетная отправка запросов.

        Args:
            metric: Имя метрики (строка) или список имен метрик
            chunk_size: Размер пакета для групповой отправки запросов (по умолчанию 50)

        Returns:
            Словарь вида {metric_name: [(timestamp, value), ...]},
            отсортированный по timestamp
        """
        result = {}
        
        # Превращаем в список для единообразия, если пришла строка
        metrics_to_query = [metric] if isinstance(metric, str) else metric
        if not metrics_to_query:
            return {}
        
        for i in range(0, len(metrics_to_query), chunk_size):
            chunk = metrics_to_query[i:i + chunk_size]

            query_string = f"get {' '.join(chunk)}\n"

            
            # t = time()
            raw_response = self.send(query_string)
            # print(f"Time In client - {time()-t}")

            lines = raw_response.splitlines()
            
            for line in lines[1:]:
                parts = line.split()
                if len(parts) != 3:
                    continue
                try:
                    m_name, value, timestamp = parts
                    if m_name not in result:
                        result[m_name] = []
                    result[m_name].append((int(timestamp), float(value)))
                except ValueError as error:
                    # Если одна строка битая, не роняем всё, а логируем
                    continue 
        # print(f"Not raw result: {result}")
        # Сортировка
        for metric_name in result:
            result[metric_name].sort(key=lambda x: x[0])

        return result

    def get_names(self) -> "List[str]":
        """Запрашивает список имен метрик через команду list"""
        raw_response = self.send("list\n") 
        if not raw_response:
            return []
        # Ответ сервера: "ok\nmetric1\nmetric2\n\n",
        return sorted(raw_response.splitlines())
