#!/usr/bin/env bash
# Скрипт установки и запуска CPU монитора
# Создает виртуальное окружение, устанавливает пакет и запускает агент сбора метрик

set -e  # Выход при ошибке

# Переход в директорию скрипта
cd "$(dirname "$0")"

VENV_DIR=".venv_cpu_monitor"

# Создание виртуального окружения если отсутствует
if [ ! -d "$VENV_DIR" ]; then
  python3 -m venv "$VENV_DIR"
fi

# Обновление pip и установка пакета
"$VENV_DIR/bin/python" -m pip install --upgrade pip
"$VENV_DIR/bin/python" -m pip install .

# Настройка переменных окружения
export METRICS_API_URL="http://localhost:8000"
export CPU_COLLECTION_INTERVAL="1"
# export CPU_SCRAPE_INTERVAL="4"
export BATCH_SEND_INTERVAL="4.5"
export COMPRESSOR_MAX_LEN=30
export CPU_COMPRESSOR="sausage_links"

# Запуск агента
exec "$VENV_DIR/bin/cpu-monitor"