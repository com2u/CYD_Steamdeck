#!/bin/bash
echo "==================================="
echo "Set final.py as main.py on ESP32"
echo "==================================="
echo

# Set the port (change if needed)
PORT="/dev/ttyUSB0"

echo "Connecting to ESP32 on $PORT and setting final.py as main.py..."
echo

python -m mpremote connect $PORT cp final.py :main.py

echo
echo "Verifying files on ESP32..."
python -m mpremote connect $PORT ls

echo
echo "Resetting ESP32..."
python -m mpremote connect $PORT reset

echo
echo "==================================="
echo "final.py has been set as main.py"
echo "The ESP32 will now run final.py on startup"
echo "==================================="
