@echo off
echo ===================================
echo ESP32-2432S028R Run Final Application
echo ===================================
echo.

REM Set the COM port (change if needed)
set PORT=COM7

echo Connecting to ESP32 on %PORT% and running final.py...
echo.

python -m mpremote connect %PORT% run final.py

echo.
echo ===================================
echo Press Ctrl+C to exit
echo ===================================
