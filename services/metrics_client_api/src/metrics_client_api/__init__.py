"""
Модуль client API для работы с сервером метрик.

Запуск:
    uvicorn metrics_client_api.main:app --host 0.0.0.0 --port 8000

Опции окружения:
    METRICS_SERVER_HOST - Хост сервера метрик (по умолчанию: metrics_server)
    METRICS_SERVER_PORT - Порт сервера метрик (по умолчанию: 8888)
    METRICS_DEFAULT_INTERVAL - Интервал обновления по умолчанию (по умолчанию: 5)
    METRICS_DEFAULT_MINUTES - Глубина истории по умолчанию (по умолчанию: 15)
"""
__author__: str = "Lex Huan"
__email__: str = "BrightComes@mail.ru"
__version__: str = "0.1.0"

from .main import app

__all__: list[str] = ["app"]
