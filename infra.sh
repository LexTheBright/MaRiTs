#!/usr/bin/env bash
# Скрипт для запуска всей инфраструктуры мониторинга
# Запускает сервер метрик, API, монитор CPU и веб-дашборд

# Функция корректной остановки всех сервисов
cleanup() {
    echo "Остановка сервисов..."
    kill $(jobs -p) 2>/dev/null
}

# Выполнить cleanup при выходе (EXIT) или прерывании (SIGINT, SIGTERM)
trap cleanup EXIT INT TERM

# Запуск сервера метрик (InfluxDB + TCP сервер на порту 8888)
source services/metrics_server/.env/bin/activate
python3 -m server.main&

# Запуск FastAPI клиента для доступа к метрикам (порт 8000)
source services/metrics_client_api/.env/bin/activate
METRICS_SERVER_HOST=localhost uvicorn metrics_client_api.main:app --host 0.0.0.0 --port 8000 --reload&

# Запуск агента сбора CPU-метрик
source services/cpu_monitor/.env/bin/activate
./services/cpu_monitor/install_and_run.sh&

# Запуск веб-дашборда (статический сервер на порту 4000)
source services/web_dashboard/.env/bin/activate
python3 services/web_dashboard/src/web_dashboard/server.py


echo "Инфраструктура запущена. Нажмите Ctrl+C для остановки."
wait