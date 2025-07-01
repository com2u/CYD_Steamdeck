@echo off
echo ===================================
echo ESP32 PC Communication Service
echo ===================================
echo.
echo Installing dependencies if needed...
pip install -r requirements.txt
echo.
echo Starting PC Service...
echo Press Ctrl+C to stop the service
echo.
python pc_service.py
pause
