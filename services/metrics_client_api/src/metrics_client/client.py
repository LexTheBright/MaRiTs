"""Реализация клиента для сервера метрик"""

import socket
from time import time
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Dict, List, Optional, Tuple


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
    """Класс клиент для сервера метрик"""

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

    def get(self, metric: "str") -> "Dict[str,List[Tuple[int,float]]]":
        """Метод получения данных"""

        result: "Dict[str,List[Tuple[int,float]]]" = {}

        for line in self.send(f"get {metric}\n").splitlines():
            try:
                _metric, value, timestamp = line.split()

                if not _metric in result:
                    result[_metric] = []

                result[_metric].append((int(timestamp), float(value)))

            except ValueError as error:
                raise ClientProtocolError(line) from error

        for item in result.items():
            item[1].sort(key=lambda stamp: stamp[0])

        return result
