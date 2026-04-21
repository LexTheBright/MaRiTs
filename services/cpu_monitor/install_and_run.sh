# #!/usr/bin/env bash
# set -e

# # Переходим в каталог скрипта (cpu_monitor)
# cd "$(dirname "$0")"

# # Устанавливаем пакет в профиль пользователя (~/.local) без sudo
# python3 -m pip install --user .

# if [ $? -ne 0 ]; then
#   echo "Ошибка установки пакета cpu-monitor"
#   exit 1
# fi

# # Добавляем локальный bin в PATH для текущей сессии
# export PATH="$HOME/.local/bin:$PATH"

# # Настройка переменных окружения (подправь под свой API)
# export METRICS_API_URL="http://localhost:8888"
# export CPU_SCRAPE_INTERVAL="5"
# export CPU_COMPRESSOR="none"

# # Запускаем агент
# cpu-monitor

#!/usr/bin/env bash
set -e

cd "$(dirname "$0")"

VENV_DIR=".venv_cpu_monitor"

if [ ! -d "$VENV_DIR" ]; then
  python3 -m venv "$VENV_DIR"
fi

"$VENV_DIR/bin/python" -m pip install --upgrade pip
"$VENV_DIR/bin/python" -m pip install .

export METRICS_API_URL="http://localhost:8000"
export CPU_SCRAPE_INTERVAL="4"
export CPU_COMPRESSOR="none"

exec "$VENV_DIR/bin/cpu-monitor"