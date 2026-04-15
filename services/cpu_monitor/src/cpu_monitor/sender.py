"""Отправитель метрик"""
from typing import Dict, List, Tuple

import requests 

MetricPoints = Dict[str, List[Tuple[int, float]]]


def send_points_batch(points: MetricPoints, api_url: str) -> None:
    """
    Отправляет пакет метрик в /metrics/put_batch.

    Формат JSON:
      [
        {"metric": "cpu.usage_percent", "value": 42.5, "timestamp": 1711450000},
        {"metric": "cpu.freq.current_mhz", "value": 2300.0, "timestamp": 1711450000},
        ...
      ]
    """
    endpoint = api_url.rstrip("/") + "/metrics/put_batch"

    payload = []
    for metric_name, items in points.items():
        for ts, value in items:
            payload.append(
                {
                    "metric": metric_name,
                    "value": value,
                    "timestamp": ts,
                }
            )

    if not payload:
        return

    resp = requests.post(endpoint, json=payload, timeout=20)
    if not resp.ok:
        raise RuntimeError(
            f"ERROR:Ошибка посылки пакета: {resp.status_code} {resp.text}"
        )
