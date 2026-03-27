## Как использовать:

```bash
chmod +x install_and_run.sh
./install_and_run.sh
```

## Дальше можно запускать только агент:

```bash
export METRICS_API_URL="http://localhost:8000"
export CPU_SCRAPE_INTERVAL="5"
export CPU_COMPRESSOR="none"
cpu-monitor
```