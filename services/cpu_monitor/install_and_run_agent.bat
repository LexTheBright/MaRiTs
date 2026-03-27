echo off
REM Переходим в каталог скрипта (cpu_monitor)
cd /d "%~dp0"

REM Устанавливаем пакет в профиль пользователя
python3 -m pip install --user .

IF %ERRORLEVEL% NEQ 0 (
    echo Ошибка установки пакета cpu-monitor.
    pause
    exit /b 1
)

REM Настраиваем переменные окружения для текущего запуска
set METRICS_API_URL=http://localhost:8000
set CPU_SCRAPE_INTERVAL=5
set CPU_COMPRESSOR=none

REM Запускаем агент
cpu-monitor

pause