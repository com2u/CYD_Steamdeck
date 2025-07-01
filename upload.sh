#!/bin/bash

echo "==================================="
echo "ESP32-2432S028R MicroPython Uploader"
echo "==================================="
echo

# Set the port (change if needed)
PORT="/dev/ttyUSB0"  # Default for Linux
# Check if we're on macOS
if [[ "$OSTYPE" == "darwin"* ]]; then
    PORT="/dev/cu.SLAB_USBtoUART"  # Common port for ESP32 on macOS
fi

# Install mpremote
echo "Installing mpremote..."
pip install mpremote
if [ $? -ne 0 ]; then
    echo "Failed to install mpremote. Please install it manually with:"
    echo "pip install mpremote"
    read -p "Press Enter to exit..."
    exit 1
fi

echo
echo "Uploading files to ESP32 on $PORT..."
echo

echo "1/6 Uploading boot.py..."
python -m mpremote connect $PORT cp boot.py :boot.py
if [ $? -ne 0 ]; then
    echo "Failed to upload boot.py"
    ERROR=1
fi

echo "2/6 Uploading ili9341.py..."
python -m mpremote connect $PORT cp ili9341.py :ili9341.py
if [ $? -ne 0 ]; then
    echo "Failed to upload ili9341.py"
    ERROR=1
fi

echo "3/6 Uploading xpt2046.py..."
python -m mpremote connect $PORT cp xpt2046.py :xpt2046.py
if [ $? -ne 0 ]; then
    echo "Failed to upload xpt2046.py"
    ERROR=1
fi

echo "4/8 Uploading test.py..."
python -m mpremote connect $PORT cp test.py :test.py
if [ $? -ne 0 ]; then
    echo "Failed to upload test.py"
    ERROR=1
fi

echo "5/8 Uploading button.py..."
python -m mpremote connect $PORT cp button.py :button.py
if [ $? -ne 0 ]; then
    echo "Failed to upload button.py"
    ERROR=1
fi

echo "6/8 Uploading display.py..."
python -m mpremote connect $PORT cp display.py :display.py
if [ $? -ne 0 ]; then
    echo "Failed to upload display.py"
    ERROR=1
fi

echo "7/9 Uploading commands.py..."
python -m mpremote connect $PORT cp commands.py :commands.py
if [ $? -ne 0 ]; then
    echo "Failed to upload commands.py"
    ERROR=1
fi

echo "8/9 Uploading audio.py..."
python -m mpremote connect $PORT cp audio.py :audio.py
if [ $? -ne 0 ]; then
    echo "Failed to upload audio.py"
    ERROR=1
fi

echo "9/9 Uploading main.py..."
python -m mpremote connect $PORT cp main.py :main.py
if [ $? -ne 0 ]; then
    echo "Failed to upload main.py"
    ERROR=1
fi

if [ -z "$ERROR" ]; then
    echo
    echo "Verifying files on ESP32..."
    python -m mpremote connect $PORT ls
    if [ $? -ne 0 ]; then
        echo "Failed to list files"
        ERROR=1
    fi

    echo
    echo "Upload complete!"
    echo
    echo "Resetting ESP32..."
    python -m mpremote connect $PORT reset
    if [ $? -ne 0 ]; then
        echo "Failed to reset ESP32. Please press the reset button on the device."
    fi

    echo
    echo "==================================="
    echo "All files uploaded successfully!"
    echo
    echo "The ESP32 should now boot with the button interface."
    echo "After power cycle, main.py should run automatically."
    echo "==================================="
else
    echo
    echo "==================================="
    echo "Error occurred during upload!"
    echo
    echo "Troubleshooting tips:"
    echo "- Make sure the ESP32 is connected to $PORT"
    echo "- Check that no other program is using the port"
    echo "- Try pressing the reset button on the ESP32"
    echo "- Some ESP32 boards require holding the BOOT button while pressing reset"
    echo "- On Linux, you may need to set permissions: sudo chmod 666 $PORT"
    echo "==================================="
fi

read -p "Press Enter to exit..."
