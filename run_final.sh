#!/bin/bash
echo "==================================="
echo "ESP32-2432S028R Run Final Application"
echo "==================================="
echo

# Set the port (change if needed)
PORT="/dev/ttyUSB0"

echo "Connecting to ESP32 on $PORT and running final.py..."
echo

python -m mpremote connect $PORT run final.py

echo
echo "==================================="
echo "Press Ctrl+C to exit"
echo "==================================="
