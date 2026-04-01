import os
from time import time
from typing import Dict, List, Tuple

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

#from src.metrics_client import Client, ClientError
from metrics_client import Client, ClientError
from .models import PutMetricRequest, MetricPoint, GetMetricResponse, PutMetricBatchItem, MetricNamesResponse, MetricSeriesResponse

app = FastAPI(title="Metrics Client API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:4000",
        "http://127.0.0.1:4000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#  Перенести в env да
METRICS_SERVER_HOST = os.getenv("METRICS_SERVER_HOST", "metrics_server")
METRICS_SERVER_PORT = int(os.getenv("METRICS_SERVER_PORT", "8888"))

client = Client(host=METRICS_SERVER_HOST, port=METRICS_SERVER_PORT, timeout=5)

# Вспомогательная фигня 

def _filter_last_minutes(points: List[tuple[int, float]], minutes: int) -> List[MetricPoint]:
    cutoff = int(time()) - minutes * 60
    result: List[MetricPoint] = []
    for ts, value in points:
        if ts >= cutoff:
            result.append(MetricPoint(timestamp=ts, value=value))
    return result


# Эндпоинты

@app.get("/metrics/names", response_model=MetricNamesResponse)
async def get_metric_names():
    try:
        data = client.get("*")
    except ClientError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    names = sorted(data.keys())
    return MetricNamesResponse(metrics=names)
                               


@app.get("/metrics/{metric_name}", response_model=MetricSeriesResponse)
async def get_metric(
    metric_name: str,
    minutes: int = Query(default=30, ge=1, le=24 * 60)
    ):
    try:
        data = client.get(metric_name)
    except ClientError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    print(f"[metrics] requested={metric_name}")
    print(f"[metrics] raw keys={list(data.keys())}")
    
    points: List[MetricPoint] = []
    if metric_name in data:
        points = _filter_last_minutes(data[metric_name], minutes)

    return MetricSeriesResponse(metric=metric_name, points=points)
    # converted: Dict[str, List[MetricPoint]] = {}
    # for key, points in data.items():
    #     converted[key] = [
    #         MetricPoint(timestamp=ts, value=val) for ts, val in points
    #     ]

    # return GetMetricResponse(metrics=converted)


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


@app.post("/metrics/put_batch", status_code=204)
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
