@echo off
echo ============================================================
echo   ESP32 CYD PC Service Startup
echo   Starting service on COM7...
echo ============================================================
echo.

cd /d "%~dp0"

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7 or later
    pause
    exit /b 1
)

REM Check if required packages are installed
python -c "import serial, psutil" >nul 2>&1
if errorlevel 1 (
    echo Installing required packages...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install required packages
        pause
        exit /b 1
    )
)

echo Starting ESP32 CYD PC Service...
echo.
echo Commands available while running:
echo   status  - Show service status
echo   test    - Send test message to ESP32
echo   update  - Force system update
echo   port    - Change serial port
echo   help    - Show help
echo   quit    - Stop the service
echo.
echo Press Ctrl+C to exit
echo.

python main.py --port COM7

echo.
echo Service stopped.
