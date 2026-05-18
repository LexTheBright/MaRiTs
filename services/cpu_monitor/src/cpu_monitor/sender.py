"""Отправитель метрик"""
from typing import Dict, List, Tuple

import requests 

MetricPoints = Dict[str, List[Tuple[int, float]]]


def send_points_batch(points: MetricPoints, api_url: str) -> None:
    """
    Отправляет пакет метрик в /metrics/put_batch.

    Преобразует словарь метрик в формат JSON и отправляет POST-запросом
    на указанный API URL.

    Args:
        points: Словарь метрик вида {metric_name: [(timestamp, value), ...]}
        api_url: Базовый URL API сервера метрик

    Raises:
        RuntimeError: Если отправка не удалась (статус ответа не 2xx)
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

    resp = requests.post(endpoint, json=payload, timeout=5.0)
    if not resp.ok:
        raise RuntimeError(
            f"Failed to send metrics batch: {resp.status_code} {resp.text}"
        )

