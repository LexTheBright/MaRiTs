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
if errorlevel 1 (
    echo Failed to upgrade pip.
    pause
    exit /b 1
)

"%VENV_DIR%\Scripts\python.exe" -m pip install .
if errorlevel 1 (
    echo Failed to install cpu-monitor.
    pause
    exit /b 1
)

echo Installation complete.
pause