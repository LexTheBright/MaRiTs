const API_BASE = window.METRICS_API_BASE || "http://localhost:8000";
const DEFAULT_MINUTES = 30;
const REFRESH_MS = 10_000;

class MetricsDashboard extends HTMLElement {
  constructor() {
    super();
    this.charts = new Map();
    this.metrics = [];
    this.timer = null;
    this.selectedMetric = "";
}

connectedCallback() {
    if (!this.shadowRoot) this.attachShadow({ mode: "open" });
    this.render();
    this.init();
  }

  disconnectedCallback() {
    this.stopAutoRefresh();
    this.destroyCharts();
  }

  render() {
    this.shadowRoot.innerHTML = `
      <style>
        :host {
          display: block;
          box-sizing: border-box;
          color: #e5e7eb;
          font-family: Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        }

        .shell {
          min-height: 100vh;
          background: linear-gradient(180deg, #0b1020 0%, #0f172a 100%);
          padding: 20px;
        }

        .topbar {
          display: flex;
          gap: 12px;
          align-items: center;
          flex-wrap: wrap;
          margin-bottom: 16px;
        }

        .brand {
          font-size: 20px;
          font-weight: 700;
          letter-spacing: 0.2px;
          margin-right: auto;
        }

        .control {
          background: #111827;
          border: 1px solid #243042;
          color: #e5e7eb;
          border-radius: 10px;
          padding: 10px 12px;
          outline: none;
        }

        .button {
          cursor: pointer;
          transition: 0.15s ease;
        }

        .button:hover {
          transform: translateY(-1px);
          background: #1f2937;
        }

        .meta {
          color: #94a3b8;
          font-size: 13px;
        }

        .grid {
          display: grid;
          grid-template-columns: 1fr;
          gap: 16px;
        }

        .card {
          background: rgba(15, 23, 42, 0.9);
          border: 1px solid #223046;
          border-radius: 16px;
          padding: 16px;
          box-shadow: 0 20px 40px rgba(0, 0, 0, 0.22);
        }

        .card-head {
          display: flex;
          justify-content: space-between;
          align-items: center;
          gap: 12px;
          margin-bottom: 12px;
        }

        .card-title {
          font-size: 16px;
          font-weight: 700;
        }

        .card-subtitle {
          font-size: 12px;
          color: #94a3b8;
        }

        .chart-wrap {
          position: relative;
          width: 100%;
          height: 320px;
        }

        canvas {
          display: block;
          width: 100% !important;
          height: 100% !important;
        }

        .empty {
          color: #94a3b8;
          font-size: 14px;
          padding: 8px 0;
        }
      </style>

      <div class="shell">
        <div class="topbar">
          <div class="brand">Metrics Dashboard</div>

          <select class="control" id="metricSelect">
            <option>Loading...</option>
          </select>

          <button class="control button" id="refreshBtn">Refresh</button>

          <label class="control" style="display:flex; align-items:center; gap:8px;">
            <input type="checkbox" id="autoRefresh" checked />
            Auto refresh
          </label>

          <div class="meta" id="status">Idle</div>
        </div>

        <div class="grid" id="charts"></div>
      </div>
    `;

    this.metricSelect = this.shadowRoot.getElementById("metricSelect");
    this.refreshBtn = this.shadowRoot.getElementById("refreshBtn");
    this.autoRefresh = this.shadowRoot.getElementById("autoRefresh");
    this.status = this.shadowRoot.getElementById("status");
    this.chartsRoot = this.shadowRoot.getElementById("charts");

    this.refreshBtn.addEventListener("click", () => this.refreshAll());
    this.metricSelect.addEventListener("change", () => {
      this.selectedMetric = this.metricSelect.value;
      this.refreshAll();
    });
    this.autoRefresh.addEventListener("change", () => {
      if (this.autoRefresh.checked) {
        this.startAutoRefresh();
      } else {
        this.stopAutoRefresh();
      }
    });
  }

  async init() {
    await this.loadMetricNames();
    this.renderChartsShell();
    await this.refreshAll();
    this.startAutoRefresh();
  }

  async apiGet(path) {
    const resp = await fetch(`${API_BASE}${path}`);
    if (!resp.ok) {
      throw new Error(`HTTP ${resp.status}: ${await resp.text()}`);
    }
    return resp.json();
  }

  async loadMetricNames() {
    this.setStatus("Loading metric names...");
    try {
      const data = await this.apiGet("/metrics/names");
      this.metrics = Array.isArray(data.metrics) ? data.metrics : [];
      this.selectedMetric = this.metrics[0] || "";
      this.metricSelect.innerHTML = "";

      for (const name of this.metrics) {
        const opt = document.createElement("option");
        opt.value = name;
        opt.textContent = name;
        this.metricSelect.appendChild(opt);
      }

      if (this.selectedMetric) {
        this.metricSelect.value = this.selectedMetric;
      }
      this.setStatus(`Loaded ${this.metrics.length} metrics`);
    } catch (err) {
      console.error(err);
      this.setStatus("Failed to load metrics");
      this.metricSelect.innerHTML = `<option value="">No metrics</option>`;
    }
  }

  renderChartsShell() {
    const preferred = [
      "cpu.usage_percent",
      "cpu.freq.current_mhz",
      "memory.percent_usage",
      "memory.used",
      "cpu.temp.celsius",
    ];

    const cpuCores = this.metrics.filter((m) => m.startsWith("cpu.core") && m.endsWith("_usage_percent"));
    const names = [
      ...preferred.filter((name) => this.metrics.includes(name)),
      ...cpuCores,
    ];

    const rest = this.metrics.filter((m) => !names.includes(m));
    this.visibleMetrics = [...names, ...rest].slice(0, 8);

    this.chartsRoot.innerHTML = "";

    for (const metric of this.visibleMetrics) {
      const card = document.createElement("div");
      card.className = "card";
      card.dataset.metric = metric;
      card.innerHTML = `
        <div class="card-head">
          <div>
            <div class="card-title">${metric}</div>
            <div class="card-subtitle">Last ${DEFAULT_MINUTES} minutes</div>
          </div>
          <div class="meta" data-last="${metric}">Waiting for data...</div>
        </div>
        <div class="chart-wrap">
          <canvas></canvas>
        </div>
        <div class="empty" data-empty="${metric}" style="display:none;">No points in selected window</div>
      `;
      this.chartsRoot.appendChild(card);
    }
  }

  async refreshAll() {
    if (!this.metrics.length) return;

    this.setStatus("Refreshing...");
    const tasks = this.visibleMetrics.map((metric) => this.loadAndRender(metric));
    await Promise.allSettled(tasks);
    this.setStatus(`Updated at ${new Date().toLocaleTimeString()}`);
  }

  async loadAndRender(metric) {
    try {
      const data = await this.apiGet(`/metrics/${encodeURIComponent(metric)}?minutes=${DEFAULT_MINUTES}`);
      const points = Array.isArray(data.points) ? data.points : [];
      this.renderChart(metric, points);
      this.updateCardState(metric, points);
    } catch (err) {
      console.error(metric, err);
      this.updateCardError(metric, err);
    }
  }

  updateCardState(metric, points) {
    const lastEl = this.shadowRoot.querySelector(`[data-last="${metric}"]`);
    const emptyEl = this.shadowRoot.querySelector(`[data-empty="${metric}"]`);
    if (lastEl) {
      if (points.length) {
        const last = points[points.length - 1];
        lastEl.textContent = `${last.value.toFixed(2)} @ ${new Date(last.timestamp * 1000).toLocaleTimeString()}`;
      } else {
        lastEl.textContent = "No data";
      }
    }
    if (emptyEl) {
      emptyEl.style.display = points.length ? "none" : "block";
    }
  }

  updateCardError(metric, err) {
    const lastEl = this.shadowRoot.querySelector(`[data-last="${metric}"]`);
    if (lastEl) lastEl.textContent = "Error";
    const emptyEl = this.shadowRoot.querySelector(`[data-empty="${metric}"]`);
    if (emptyEl) {
      emptyEl.style.display = "block";
      emptyEl.textContent = `Failed to load: ${err.message}`;
    }
  }

  renderChart(metric, points) {
    const card = this.shadowRoot.querySelector(`[data-metric="${metric}"]`);
    if (!card) return;

    const canvas = card.querySelector("canvas");
    const dataset = points.map((p) => ({
      x: p.timestamp * 1000,
      y: p.value,
    }));

    const existing = this.charts.get(metric);
    if (existing) {
      existing.data.datasets[0].data = dataset;
      existing.update();
      return;
    }

    const color = this.colorForMetric(metric);

    const chart = new Chart(canvas, {
      type: "line",
      data: {
        datasets: [
          {
            label: metric,
            data: dataset,
            borderColor: color,
            backgroundColor: color + "33",
            fill: false,
            tension: 0.25,
            borderWidth: 2,
            pointRadius: 1.5,
            pointHoverRadius: 4,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        animation: false,
        interaction: {
          mode: "index",
          intersect: false,
        },
        plugins: {
          legend: {
            display: false,
          },
          tooltip: {
            callbacks: {
              title(items) {
                return items.length ? new Date(items[0].parsed.x).toLocaleString() : "";
              },
            },
          },
        },
        scales: {
          x: {
            type: "time",
            time: {
              tooltipFormat: "yyyy-MM-dd HH:mm:ss",
            },
            ticks: {
              color: "#94a3b8",
            },
            grid: {
              color: "rgba(148, 163, 184, 0.12)",
            },
          },
          y: {
            ticks: {
              color: "#94a3b8",
            },
            grid: {
              color: "rgba(148, 163, 184, 0.12)",
            },
          },
        },
      },
    });

    this.charts.set(metric, chart);
  }

  colorForMetric(metric) {
    const palette = [
      "#60a5fa",
      "#34d399",
      "#f59e0b",
      "#f472b6",
      "#a78bfa",
      "#22c55e",
      "#fb7185",
      "#38bdf8",
    ];
    let hash = 0;
    for (let i = 0; i < metric.length; i++) hash = (hash * 31 + metric.charCodeAt(i)) >>> 0;
    return palette[hash % palette.length];
  }

  destroyCharts() {
    for (const chart of this.charts.values()) {
      chart.destroy();
    }
    this.charts.clear();
  }

  startAutoRefresh() {
    this.stopAutoRefresh();
    this.timer = setInterval(() => this.refreshAll(), REFRESH_MS);
  }

  stopAutoRefresh() {
    if (this.timer) {
      clearInterval(this.timer);
      this.timer = null;
    }
  }

  setStatus(text) {
    if (this.status) this.status.textContent = text;
  }
}

customElements.define("metrics-dashboard", MetricsDashboard);