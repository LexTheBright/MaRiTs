from typing import Literal, Dict, List, Tuple

CompressorName = Literal["none"] 

MetricPoints = Dict[str, List[Tuple[int, float]]]


def compress_points(
    points: MetricPoints,
    compressor_name: CompressorName = "none",
) -> MetricPoints:
    """
    Пока будущая точка расширения.

    Структура: {metric_name: [(ts, value), ...], ...}
    """
    if compressor_name == "none":
        return points

    # здесь можно будет добавить реальные алгоритмы
    return points