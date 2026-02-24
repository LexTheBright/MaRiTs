"""Реализация сервера для приема метрик"""

from asyncio import Protocol, get_event_loop
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Dict, List, Tuple

g_storage: "Dict[str,List[Tuple[int,float]]]" = {}


class ClientServerProtocol(Protocol):
    """Реализация протокола"""

    def connection_made(self, transport):
        """connection_made"""

        self.transport = transport

    def data_received(self, data):
        """Обработка поступивших данных"""

        result: "str" = "error\nwrong command\n\n"
        command: "str" = data.decode("utf-8").strip("\r\n")

        chunks: "List[str]" = command.split(" ")

        if chunks[0] == "get":
            result = "ok\n"

            if chunks[1] == "*":
                for key, values in g_storage.items():
                    for value in values:
                        result += f"{key} {value[1]} {value[0]}\n"

            else:
                if chunks[1] in g_storage:
                    for value in g_storage[chunks[1]]:
                        result += f"{chunks[1]} {value[1]} {value[0]}\n"

            result += "\n"

        elif chunks[0] == "put":
            if chunks[1] == "*":
                result = "error\nkey cannot contain *\n\n"

            else:
                if not chunks[1] in g_storage:
                    g_storage[chunks[1]] = []

                try:
                    timestamp: "int" = int(chunks[3])
                    value: "float" = float(chunks[2])

                    if not (timestamp, value) in g_storage[chunks[1]]:
                        g_storage[chunks[1]].append((timestamp, value))
                        g_storage[chunks[1]].sort(key=lambda item: item[0])

                    result = "ok\n\n"

                except ValueError:
                    result = "error\nvalue error\n\n"

        self.transport.write(result.encode("utf-8"))


def run_server(host: "str", port: "int") -> None:
    """Запуск сервера"""

    loop = get_event_loop()
    coro = loop.create_server(ClientServerProtocol, host, port)
    server = loop.run_until_complete(coro)

    try:
        loop.run_forever()

    except KeyboardInterrupt:
        ...

    server.close()
    loop.run_until_complete(server.wait_closed())
    loop.close()


if __name__ == "__main__":
    run_server("127.0.0.1", 8888)
