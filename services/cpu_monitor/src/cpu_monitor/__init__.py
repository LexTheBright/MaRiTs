"""
Модуль мониторинга CPU.

Собирает метрики использования CPU, частоты, температуры и памяти,
сжимает их и отправляет на сервер метрик.

Запуск:
    python -m cpu_monitor.main

Опции окружения:
    METRICS_API_URL - URL сервера метрик (по умолчанию: http://localhost:8000)
    CPU_COLLECTION_INTERVAL - Интервал сбора метрик в секундах (по умолчанию: 0.5)
    BATCH_SEND_INTERVAL - Интервал отправки пакетов в секундах (по умолчанию: 3.0)
    CPU_COMPRESSOR - Тип компрессора: "none" или "sausage_links" (по умолчанию: none)
    COMPRESSOR_DEVIATION - Отклонение для сжатия (по умолчанию: 1.0)
    COMPRESSOR_AUTO_DEV_FACTOR - Фактор авто-отклонения (по умолчанию: 0.5)
    COMPRESSOR_EMA_ALPHA - Коэффициент сглаживания EMA (по умолчанию: 0.3)
    COMPRESSOR_MAX_SILENT_INTERVAL - Максимальный интервал молчания для heartbeat (по умолчанию: 20.0)
"""

__author__: str = "Lex Huan"
__email__: str = "BrightComes@mail.ru"
__version__: str = "0.1.0"

# src/cpu_monitor/__init__.py
# from .main import run_agent

# __all__ = ["run_agent"]

