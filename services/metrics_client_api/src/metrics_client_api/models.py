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


class MetricStat(BaseModel):
    mean: float
    std: float
    trend: float  # Наклон линии тренда
    min_val: float
    max_val: float
    last_value: float
    is_increasing: bool

class AnalysisResponse(BaseModel):
    stats: Dict[str, MetricStat]

class PutMetricBatchItem(BaseModel):
    metric: str
    value: float
    timestamp: int | None = None

class MetricSeriesResponse(BaseModel):
    metric: str
    points: List[MetricPoint]


class MetricNamesResponse(BaseModel):
    metrics: List[str]
