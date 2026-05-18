"""
Модуль сервера метрик.

Запуск:
    python -m metrics_server.server.main

Опции окружения:
    INFLUX_URL - URL InfluxDB (по умолчанию: http://localhost:8086)
    INFLUX_TOKEN - Токен доступа к InfluxDB
    INFLUX_ORG - Организация в InfluxDB (по умолчанию: MaRiTs)
    INFLUX_BUCKET - Bucket для хранения метрик (по умолчанию: cpu-metrics)
"""

__author__: str = "Lex Huan"
__email__: str = "BrightComes@mail.ru"
__version__: str = "0.1.0"

from .main import ClientServerProtocol

__all__ = ["ClientServerProtocol"]
