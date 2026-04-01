@echo off
setlocal

cd /d "%~dp0"

set VENV_DIR=.venv_cpu_monitor

if not exist "%VENV_DIR%" (
    python -m venv "%VENV_DIR%"
    if errorlevel 1 (
        echo Failed to create virtual environment.
        pause
        exit /b 1
    )
)

"%VENV_DIR%\Scripts\python.exe" -m pip install --upgrade pip
"%VENV_DIR%\Scripts\python.exe" -m pip install .

set METRICS_API_URL=http://localhost:8000
set CPU_SCRAPE_INTERVAL=5
set CPU_COMPRESSOR=none

"%VENV_DIR%\Scripts\python.exe" -m cpu_monitor.main
pause