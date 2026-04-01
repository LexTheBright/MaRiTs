@echo off
setlocal

cd /d "%~dp0"

set VENV_DIR=.venv_cpu_monitor

if not exist "%VENV_DIR%\Scripts\python.exe" (
    echo Virtual environment not found. Run install.bat first.
    pause
    exit /b 1
)

set METRICS_API_URL=http://localhost:8000
set CPU_SCRAPE_INTERVAL=5
set CPU_COMPRESSOR=none

"%VENV_DIR%\Scripts\cpu-monitor.exe"
if errorlevel 1 (
    echo Failed to start cpu-monitor.
    pause
    exit /b 1
)

pause