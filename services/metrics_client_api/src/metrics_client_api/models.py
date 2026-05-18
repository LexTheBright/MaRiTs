"""
Модели данных для API метрик.

Содержит Pydantic модели для запросов и ответов API.
"""

from datetime import datetime
from random import randint
from typing import Annotated, Literal, Optional, Dict, List
from uuid import UUID, uuid4, uuid5

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


class PutMetricRequest(BaseModel):
    """Запрос на отправку одной метрики."""
    metric: str = Field(..., description="Название метрики")
    value: float = Field(..., description="Значение")
    timestamp: int | None = Field(
        default=None, description="UNIX‑время, если не указано — берётся текущее"
    )


class MetricPoint(BaseModel):
    """Точка данных метрики."""
    timestamp: int
    value: float


class MetricStat(BaseModel):
    """Статистика по метрике."""
    mean: float
    std: float
    trend: float  # Наклон линии тренда
    min_val: float
    max_val: float
    last_value: float
    is_increasing: bool

class AnalysisResponse(BaseModel):
    """Ответ с аналитикой по метрикам."""
    stats: Dict[str, MetricStat]

class PutMetricBatchItem(BaseModel):
    """Элемент пакета метрик для отправки."""
    metric: str
    value: float
    timestamp: int | None = None

class MetricSeriesResponse(BaseModel):
    """Ответ с временным рядом метрики."""
    metric: str
    points: List[MetricPoint]


class MetricNamesResponse(BaseModel):
    """Ответ со списком имен метрик."""
    metrics: List[str]
