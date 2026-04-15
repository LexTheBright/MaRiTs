# /// script
# [tool.marimo.display]
# theme = "dark"
# ///

import marimo as mo

__generated_with = "0.14.0"
app = mo.App(width="full")


@app.cell
def _():
    import os
    import requests
    import pandas as pd
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    import plotly.io as pio

    pio.templates.default = "plotly_dark"

    api_host = os.getenv("METRICS_CLIENT_API_HOST", "metrics_client_api")
    api_port = int(os.getenv("METRICS_CLIENT_API_PORT", "8000"))
    api_base_url = f"http://{api_host}:{api_port}"

    return os, requests, pd, go, make_subplots, pio, api_base_url


@app.cell
def _():
    import marimo as mo
    return mo


@app.cell
def _(mo, api_base_url, requests):
    def load_dashboard_config():
        try:
            response = requests.get(f"{api_base_url}/metrics/dashboard/config", timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception:
            return {
                "default_interval": 20,
                "default_minutes": 30,
                "min_interval": 5,
                "max_interval": 60,
                "min_minutes": 1,
                "max_minutes": 60,
            }

    def load_metric_names():
        try:
            response = requests.get(f"{api_base_url}/metrics/names", timeout=10)
            response.raise_for_status()
            return response.json().get("metrics", [])
        except Exception:
            return []

    config = load_dashboard_config()
    available_metrics = load_metric_names()

    cpu_defaults = [
        "cpu.core0_usage_percent",
        "cpu.core1_usage_percent",
        "cpu.core2_usage_percent",
        "cpu.core3_usage_percent",
        "cpu.usage_percent",
        "cpu.freq.current_mhz",
    ]
    other_defaults = ["memory.percent_usage", "memory.used"]

    cpu_selected_default = [m for m in cpu_defaults if m in available_metrics]
    other_selected_default = [m for m in other_defaults if m in available_metrics]

    if not cpu_selected_default:
        cpu_selected_default = [m for m in available_metrics if m.startswith("cpu.")][:6]
    if not other_selected_default:
        other_selected_default = [m for m in available_metrics if not m.startswith("cpu.")][:4]

    cpu_metrics_selector = mo.ui.multiselect(
        label="Процессорные метрики",
        options=[m for m in available_metrics if m.startswith("cpu.")],
        value=cpu_selected_default,
        full_width=True,
    )

    other_metrics_selector = mo.ui.multiselect(
        label="Память и прочие метрики",
        options=[m for m in available_metrics if not m.startswith("cpu.")],
        value=other_selected_default,
        full_width=True,
    )

    time_window = mo.ui.slider(
        label="Временное окно, минут",
        start=config["min_minutes"],
        stop=config["max_minutes"],
        step=1,
        value=config["default_minutes"],
        show_value=True,
        full_width=True,
    )

    refresh_interval = mo.ui.slider(
        label="Интервал обновления, секунд",
        start=config["min_interval"],
        stop=config["max_interval"],
        step=1,
        value=config["default_interval"],
        show_value=True,
        full_width=True,
    )

    auto_refresh = mo.ui.refresh(default_interval=f"{config['default_interval']}s")

    return (
        config,
        available_metrics,
        cpu_selected_default,
        other_selected_default,
        cpu_metrics_selector,
        other_metrics_selector,
        time_window,
        refresh_interval,
        auto_refresh,
    )


@app.cell
def _(mo, cpu_metrics_selector, other_metrics_selector, time_window, refresh_interval):
    mo.vstack(
        [
            mo.md(
                f"""
# System Monitor

- CPU метрик в панели: **{len(cpu_metrics_selector.value)}**
- Остальных метрик в панели: **{len(other_metrics_selector.value)}**
- Временное окно: **{time_window.value} мин**
- Интервал обновления: **{refresh_interval.value} сек**
"""
            ),
            mo.hstack([cpu_metrics_selector, other_metrics_selector], gap=1),
            mo.hstack([time_window, refresh_interval], gap=1),
        ],
        gap=1,
    )


@app.cell
def _(api_base_url, requests, pd, cpu_metrics_selector, other_metrics_selector, time_window, refresh_interval, auto_refresh):
    def fetch_series(metrics_list, minutes):
        if not metrics_list:
            return {}, {}

        series_data = {}
        stats_data = {}
        metrics_str = ",".join(metrics_list)

        try:
            for _metric_name in metrics_list:
                response = requests.get(
                    f"{api_base_url}/metrics/{_metric_name}",
                    params={"minutes": minutes},
                    timeout=15,
                )
                if response.ok:
                    payload = response.json()
                    points = payload.get("points", [])
                    if points:
                        _df = pd.DataFrame(points)
                        _df["timestamp"] = pd.to_datetime(_df["timestamp"], unit="s")
                        series_data[_metric_name] = _df

            response = requests.get(
                f"{api_base_url}/metrics/analysis",
                params={"metrics": metrics_str, "minutes": minutes},
                timeout=15,
            )
            if response.ok:
                stats_data = response.json().get("stats", {})
        except Exception:
            return {}, {}

        return series_data, stats_data

    _ = auto_refresh.value
    _refresh_tick = auto_refresh.value
    selected_cpu_metrics = list(cpu_metrics_selector.value) if cpu_metrics_selector.value else []
    selected_other_metrics = list(other_metrics_selector.value) if other_metrics_selector.value else []
    selected_metrics = selected_cpu_metrics + selected_other_metrics
    minutes = int(time_window.value)
    interval = int(refresh_interval.value)

    series_data, stats_data = fetch_series(selected_metrics, minutes)

    return fetch_series, selected_cpu_metrics, selected_other_metrics, selected_metrics, minutes, interval, series_data, stats_data, _refresh_tick


@app.cell
def _(series_data, go, make_subplots):
    _cpu_metrics = []
    _other_metrics = []
    for _metric_name in series_data.keys():
        if _metric_name.startswith("cpu."):
            _cpu_metrics.append(_metric_name)
        else:
            _other_metrics.append(_metric_name)

    _cpu_fig = make_subplots(
        rows=max(1, len(_cpu_metrics)),
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.08,
        subplot_titles=tuple(_cpu_metrics) if _cpu_metrics else ("CPU метрики",),
    )
    _other_fig = make_subplots(
        rows=max(1, len(_other_metrics)),
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.08,
        subplot_titles=tuple(_other_metrics) if _other_metrics else ("Остальные метрики",),
    )

    _colors = ["#38bdf8", "#22c55e", "#f97316", "#a855f7", "#ef4444", "#eab308", "#14b8a6", "#f472b6"]

    if not series_data:
        _cpu_fig = go.Figure()
        _cpu_fig.update_layout(template="plotly_dark", height=420, title="Нет CPU данных")
        _other_fig = go.Figure()
        _other_fig.update_layout(template="plotly_dark", height=420, title="Нет данных")
    else:
        for _i, _metric_name in enumerate(_cpu_metrics):
            _df = series_data[_metric_name]
            _cpu_fig.add_trace(
                go.Scatter(
                    x=_df["timestamp"],
                    y=_df["value"],
                    mode="lines",
                    name=_metric_name,
                    line=dict(color=_colors[_i % len(_colors)], width=2),
                    hovertemplate=f"<b>{_metric_name}</b><br>Время: %{{x|%Y-%m-%d %H:%M:%S}}<br>Значение: %{{y:.2f}}<extra></extra>",
                ),
                row=_i + 1,
                col=1,
            )
        for _i, _metric_name in enumerate(_other_metrics):
            _df = series_data[_metric_name]
            _other_fig.add_trace(
                go.Scatter(
                    x=_df["timestamp"],
                    y=_df["value"],
                    mode="lines",
                    name=_metric_name,
                    line=dict(color=_colors[_i % len(_colors)], width=2),
                    hovertemplate=f"<b>{_metric_name}</b><br>Время: %{{x|%Y-%m-%d %H:%M:%S}}<br>Значение: %{{y:.2f}}<extra></extra>",
                ),
                row=_i + 1,
                col=1,
            )

        _cpu_fig.update_layout(
            height=max(420, 220 * max(1, len(_cpu_metrics))),
            template="plotly_dark",
            title="Процессорные метрики",
            hovermode="x unified",
            showlegend=False,
            margin=dict(l=50, r=20, t=60, b=30),
            paper_bgcolor="#0f172a",
            plot_bgcolor="#0f172a",
        )
        _other_fig.update_layout(
            height=max(420, 220 * max(1, len(_other_metrics))),
            template="plotly_dark",
            title="Память и прочие метрики",
            hovermode="x unified",
            showlegend=False,
            margin=dict(l=50, r=20, t=60, b=30),
            paper_bgcolor="#0f172a",
            plot_bgcolor="#0f172a",
        )

    _cpu_fig


@app.cell
def _(series_data, go, make_subplots):
    _cpu_metrics = []
    _other_metrics = []
    for _metric_name in series_data.keys():
        if _metric_name.startswith("cpu."):
            _cpu_metrics.append(_metric_name)
        else:
            _other_metrics.append(_metric_name)

    _cpu_fig = make_subplots(
        rows=max(1, len(_cpu_metrics)),
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.08,
        subplot_titles=tuple(_cpu_metrics) if _cpu_metrics else ("CPU метрики",),
    )
    _other_fig = make_subplots(
        rows=max(1, len(_other_metrics)),
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.08,
        subplot_titles=tuple(_other_metrics) if _other_metrics else ("Остальные метрики",),
    )

    _colors = ["#38bdf8", "#22c55e", "#f97316", "#a855f7", "#ef4444", "#eab308", "#14b8a6", "#f472b6"]

    if not series_data:
        _cpu_fig = go.Figure()
        _cpu_fig.update_layout(template="plotly_dark", height=420, title="Нет CPU данных")
        _other_fig = go.Figure()
        _other_fig.update_layout(template="plotly_dark", height=420, title="Нет данных")
    else:
        for _i, _metric_name in enumerate(_cpu_metrics):
            _df = series_data[_metric_name]
            _cpu_fig.add_trace(
                go.Scatter(
                    x=_df["timestamp"],
                    y=_df["value"],
                    mode="lines",
                    name=_metric_name,
                    line=dict(color=_colors[_i % len(_colors)], width=2),
                    hovertemplate=f"<b>{_metric_name}</b><br>Время: %{{x|%Y-%m-%d %H:%M:%S}}<br>Значение: %{{y:.2f}}<extra></extra>",
                ),
                row=_i + 1,
                col=1,
            )
        for _i, _metric_name in enumerate(_other_metrics):
            _df = series_data[_metric_name]
            _other_fig.add_trace(
                go.Scatter(
                    x=_df["timestamp"],
                    y=_df["value"],
                    mode="lines",
                    name=_metric_name,
                    line=dict(color=_colors[_i % len(_colors)], width=2),
                    hovertemplate=f"<b>{_metric_name}</b><br>Время: %{{x|%Y-%m-%d %H:%M:%S}}<br>Значение: %{{y:.2f}}<extra></extra>",
                ),
                row=_i + 1,
                col=1,
            )

        _cpu_fig.update_layout(
            height=max(420, 220 * max(1, len(_cpu_metrics))),
            template="plotly_dark",
            title="Процессорные метрики",
            hovermode="x unified",
            showlegend=False,
            margin=dict(l=50, r=20, t=60, b=30),
            paper_bgcolor="#0f172a",
            plot_bgcolor="#0f172a",
        )
        _other_fig.update_layout(
            height=max(420, 220 * max(1, len(_other_metrics))),
            template="plotly_dark",
            title="Память и прочие метрики",
            hovermode="x unified",
            showlegend=False,
            margin=dict(l=50, r=20, t=60, b=30),
            paper_bgcolor="#0f172a",
            plot_bgcolor="#0f172a",
        )

    _other_fig


@app.cell
def _(stats_data, pd, mo):
    if not stats_data:
        mo.md("### Статистика\n\nВыберите метрики, чтобы увидеть аналитику.")
    else:
        rows = []
        for _stat_metric, stats in stats_data.items():
            rows.append(
                {
                    "Метрика": _stat_metric,
                    "Среднее": round(stats.get("mean", 0), 2),
                    "Стд. откл.": round(stats.get("std", 0), 2),
                    "Тренд": round(stats.get("trend", 0), 4),
                    "Мин": round(stats.get("min_val", 0), 2),
                    "Макс": round(stats.get("max_val", 0), 2),
                    "Последнее": round(stats.get("last_value", 0), 2),
                    "Растет": "↑" if stats.get("is_increasing", False) else "↓",
                }
            )

        stats_df = pd.DataFrame(rows)
        mo.md("### Статистика")
        stats_df


@app.cell
def _(mo, refresh_interval):
    mo.md(
        f"""
### Управление

- Автообновление включено.
- Интервал автообновления: **{refresh_interval.value} сек**.
"""
    )


if __name__ == "__main__":
    app.run()
