import os
from typing import Dict, List, Tuple

from fastapi import FastAPI, HTTPException

#from src.metrics_client import Client, ClientError
from metrics_client import Client, ClientError
from .models import PutMetricRequest, MetricPoint, GetMetricResponse, PutMetricBatchItem

app = FastAPI(title="Metrics Client API")


#  Перенести в env да
METRICS_SERVER_HOST = os.getenv("METRICS_SERVER_HOST", "metrics_server")
METRICS_SERVER_PORT = int(os.getenv("METRICS_SERVER_PORT", "8888"))

client = Client(host=METRICS_SERVER_HOST, port=METRICS_SERVER_PORT, timeout=5)

@app.get("/metrics/{metric_name}", response_model=GetMetricResponse)
async def get_metric(metric_name: str):
    try:
        data = client.get(metric_name)
    except ClientError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    converted: Dict[str, List[MetricPoint]] = {}
    for key, points in data.items():
        converted[key] = [
            MetricPoint(timestamp=ts, value=val) for ts, val in points
        ]

    return GetMetricResponse(metrics=converted)


@app.post("/metrics/put", status_code=204)
async def put_metric(payload: PutMetricRequest):
    try:
        client.put(
            metric=payload.metric,
            value=payload.value,
            timestamp=payload.timestamp,
        )
    except ClientError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return  # 204 No Content


@app.post("/metrics/batch", status_code=204)
async def put_metrics_batch(items: List[PutMetricBatchItem]):
    if not items:
        return

    try:
        for item in items:
            client.put(
                metric=item.metric,
                value=item.value,
                timestamp=item.timestamp,
            )
    except ClientError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return
