"""
Запуск:
    uvicorn metrics_client_api.main:app --host 0.0.0.0 --port 8000

Опции:
    -H, --host HOST        Хост для запуска сервера (по умолчанию: 127.0.0.1)
    -P, --port PORT        Порт для запуска сервера (по умолчанию: 8080)
    -L, --log-level LEVEL  Уровень логирования (DEBUG, INFO, WARNING, ERROR, CRITICAL)
                           (по умолчанию: WARNING)
    -D, --debug            Включение режима отладки (также включает подробное логирование)

Режим отладки:
    Режим отладки включается либо флагом -D/--debug, либо если интерпретатор запущен
    без ключей оптимизации (__debug__).
    При включенном режиме отладки (-D, --debug или __debug__) уровень логирования
    устанавливается в DEBUG, независимо от указанного в --log-level.

Примеры:
    python -O -m veche --host 0.0.0.0 --port 8000 --log-level INFO
    python -O -m veche -H 0.0.0.0 -P 8000 -L DEBUG
    python -O -m veche --debug
"""

__author__: str = "Lex Huan"
__email__: str = "BrightComes@mail.ru"
__version__: str = "0.1.0"

# src/cpu_monitor/__init__.py
from .main import run_agent

__all__ = ["run_agent"]

