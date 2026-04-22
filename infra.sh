#!/usr/bin/bash


cleanup() {
    echo "Остановка сервисов..."
    kill $(jobs -p) 2>/dev/null
}

# Выполнить cleanup при выходе (EXIT) или прерывании (SIGINT, SIGTERM)
trap cleanup EXIT INT TERM

source services/metrics_server/.env/bin/activate
python3 -m server.main&

source services/metrics_client_api/.env/bin/activate
METRICS_SERVER_HOST=localhost uvicorn metrics_client_api.main:app --host 0.0.0.0 --port 8000 --reload&


source services/cpu_monitor/.env/bin/activate
./services/cpu_monitor/install_and_run.sh&


source services/web_dashboard/.env/bin/activate
python3 services/web_dashboard/src/web_dashboard/server.py


echo "Инфраструктура запущена. Хуйните Ctrl+C для остановки."
wait