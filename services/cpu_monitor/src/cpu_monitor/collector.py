from time import time
from typing import Dict, List, Tuple

import psutil  

MetricPoints = Dict[str, List[Tuple[int, float]]]


def collect_cpu_metrics(interval: float = 5.0) -> MetricPoints:
    """
    Собирает пакет CPU-метрик за interval секунд.

    Возвращает словарь:
      {
        "cpu.usage_percent": [(ts, value)],
        "cpu.freq.current_mhz": [(ts, value)],
        "cpu.temp.celsius": [(ts, value)],  # если доступно
        ...
      }
    """
    ts = int(time())

    metrics: MetricPoints = {}

    # Общая загрузка CPU
    # usage = psutil.cpu_percent(interval=interval) 
    usage = psutil.cpu_percent(interval=interval, percpu=True)
    if type(usage) == list:
        for i, core in enumerate(usage):
            metrics[f"cpu.core{i}_usage_percent"] = [(ts, float(core))]
    usage = psutil.cpu_percent(interval=interval) 
    metrics["cpu.usage_percent"] = [(ts, usage)]

    # CPU
    try:
        freq = psutil.cpu_freq()
        if freq is not None:
            metrics["cpu.freq.current_mhz"] = [(ts, float(freq.current))]
            # при желании:
            metrics["cpu.freq.min_mhz"] = [(ts, float(freq.min))]
            metrics["cpu.freq.max_mhz"] = [(ts, float(freq.max))]
    except Exception:
        pass

    # Температура CPU (если ОС/железо это поддерживает)
    try:
        temps = psutil.sensors_temperatures()  # может вернуть {} [web:129][web:134]
        if temps:
            # берём первое подходящее значение
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