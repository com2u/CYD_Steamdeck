@echo off
echo ============================================================
echo   ESP32 CYD PC Service Installation
echo ============================================================
echo.

cd /d "%~dp0"

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo.
    echo Please install Python 3.7 or later from:
    echo https://www.python.org/downloads/
    echo.
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo Python found:
python --version
echo.

REM Check if pip is available
pip --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: pip is not available
    echo Please reinstall Python with pip included
    pause
    exit /b 1
)

echo Installing required packages...
echo.

pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo ERROR: Failed to install required packages
    echo.
    echo Try running this command manually:
    echo pip install pyserial psutil
    pause
    exit /b 1
)

echo.
echo ============================================================
echo   Installation Complete!
echo ============================================================
echo.
echo The ESP32 CYD PC Service has been installed successfully.
echo.
echo To start the service:
echo   1. Double-click start_service.bat
echo   2. Or run: python main.py --port COM7
echo.
echo Make sure your ESP32 is connected to COM7 (or change the port)
echo.
pause
