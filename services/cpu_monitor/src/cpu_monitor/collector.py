from time import time
from typing import Dict, List, Tuple

import psutil  

MetricPoints = Dict[str, List[Tuple[int, float]]]


def collect_cpu_metrics(interval: float = 5.0) -> MetricPoints:
    """
    Собирает пакет CPU-метрик за interval секунд.

    Собирает метрики загрузки CPU (общей и по ядрам), частоты,
    температуры (если доступна) и использования памяти.

    Args:
        interval: Интервал сбора метрик в секундах (по умолчанию 5.0)

    Returns:
        Словарь метрик вида:
        {
            "cpu.usage_percent": [(timestamp, значение), ...],
            "cpu.core0_usage_percent": [(timestamp, значение), ...],
            "cpu.freq.current_mhz": [(timestamp, значение), ...],
            "cpu.temp.celsius": [(timestamp, значение), ...],  # если доступно
            "memory.percent_usage": [(timestamp, значение), ...],
            "memory.used": [(timestamp, значение), ...],
        }
    """
    ts = int(time())

    metrics: MetricPoints = {}

    # Общая загрузка CPU
    usage = psutil.cpu_percent(interval=interval, percpu=True)
    if type(usage) == list:
        for i, core in enumerate(usage):
            metrics[f"cpu.core{i}_usage_percent"] = [(ts, float(core))]
    usage = psutil.cpu_percent(interval=interval) 
    metrics["cpu.usage_percent"] = [(ts, usage)]

    # Частота CPU
    try:
        freq = psutil.cpu_freq()
        if freq is not None:
            metrics["cpu.freq.current_mhz"] = [(ts, float(freq.current))]
    except Exception:
        pass

    # Температура CPU (если ОС/железо это поддерживает)
    try:
        temps = psutil.sensors_temperatures()  # может вернуть {} 
        if temps:
            for name, entries in temps.items():
                if not entries:
                    continue
                current = entries[0].current
                metrics["cpu.temp.celsius"] = [(ts, float(current))]
                break
    except Exception:
        pass

    # Память 
    try:
        memo = psutil.virtual_memory()
        if memo is not None:
            metrics["memory.percent_usage"] = [(ts, float(memo.percent))]
            metrics["memory.used"] = [(ts, float(memo.used))]
    except Exception:
        pass
    return metrics