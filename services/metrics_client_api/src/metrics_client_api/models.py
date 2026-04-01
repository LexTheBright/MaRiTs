"""
models
---------------

Различные модели для приложения.
"""

from datetime import datetime
from random import randint
from typing import Annotated, Literal, Optional, Dict, List
from uuid import UUID, uuid4, uuid5

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


class PutMetricRequest(BaseModel):
    metric: str = Field(..., description="Название метрики")
    value: float = Field(..., description="Значение")
    timestamp: int | None = Field(
        default=None, description="UNIX‑время, если не указано — берётся текущее"
    )


class MetricPoint(BaseModel):
    timestamp: int
    value: float


class GetMetricResponse(BaseModel):
    metrics: Dict[str, List[MetricPoint]]


class PutMetricBatchItem(BaseModel):
    metric: str
    value: float
    timestamp: int | None = None

class MetricSeriesResponse(BaseModel):
    metric: str
    points: List[MetricPoint]


class MetricNamesResponse(BaseModel):
    metrics: List[str]
