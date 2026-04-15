"""Реализация агента сбора и отправки метрик."""

import os
import time
from typing import Literal

from cpu_monitor.collector import collect_cpu_metrics
from cpu_monitor.compressor import compress_points, CompressorName
from cpu_monitor.sender import send_points_batch


def run_agent(
    api_url: str,
    interval: float,
    compressor_name: CompressorName = "none",
) -> None:
    print(
        f"Starting CPU monitor: api_url={api_url}, "
        f"interval={interval}s, compressor={compressor_name}"
    )

    while True:
        try:
            time.sleep(interval)

            raw_points = collect_cpu_metrics(interval=1.0)
            # print("Получили за секунду замера:", raw_points)

            points = compress_points(points=raw_points, compressor_name=compressor_name)
            # print("Получили после сжатия:", points)

            send_points_batch(points=points, api_url=api_url)
            print('Sended batch: ', points)

        except KeyboardInterrupt:
            print("Shutting down agent...")
            break
        except Exception as exc:
            print(f"Agent error: {exc}, continuing...")


def main() -> None:
    """CLI‑обёртка, читающая env‑переменные и запускающая run_agent()."""

    api_url = os.getenv("METRICS_API_URL", "http://localhost:8000")
    interval = float(os.getenv("CPU_SCRAPE_INTERVAL", "5.0"))
    # metric = os.getenv("CPU_METRIC_NAME", "cpu.usage_percent")
    compressor_name: CompressorName = os.getenv("CPU_COMPRESSOR", "none")  # type: ignore

    run_agent(
        api_url=api_url,
        interval=interval,
        # metric=metric,
        compressor_name=compressor_name,
    )


if __name__ == "__main__":
    main()
