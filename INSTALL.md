# Installation Guide for ESP32-2432S028R MicroPython Project

This guide will help you set up MicroPython on your ESP32-2432S028R (Cheap Yellow Display) and upload the project files.

## Prerequisites

- ESP32-2432S028R board
- USB cable (usually micro USB)
- Computer with VSCode installed
- Internet connection

## Step 1: Install Required Software

1. **Install Python**: Download and install Python from [python.org](https://www.python.org/downloads/) (version 3.7 or newer)

2. **Install VSCode**: Download and install Visual Studio Code from [code.visualstudio.com](https://code.visualstudio.com/download)

3. **Install Pymakr Extension**:
   - Open VSCode
   - Go to Extensions (Ctrl+Shift+X)
   - Search for "Pymakr"
   - Install the Pymakr extension by Pycom

4. **Install esptool**: Open a terminal or command prompt and run:
   ```
   pip install esptool
   ```

## Step 2: Download MicroPython Firmware

1. Go to the [MicroPython downloads page](https://micropython.org/download/esp32/)
2. Download the latest stable firmware (.bin file) for ESP32

## Step 3: Flash MicroPython to ESP32

1. Connect your ESP32 to your computer via USB
2. Identify the COM port:
   - Windows: Check Device Manager under "Ports (COM & LPT)"
   - macOS: Run `ls /dev/cu.*` in Terminal
   - Linux: Run `ls /dev/ttyUSB*` in Terminal

3. Erase the ESP32 flash (replace COM7 with your port if different):
   ```
   python -m esptool --port COM7 erase_flash
   ```

4. Flash the MicroPython firmware (replace COM7 and firmware.bin with your values):
   ```
   python -m esptool --chip esp32 --port COM7 --baud 460800 write_flash -z 0x1000 ESP32_GENERIC-20250415-v1.25.0.bin
   ```

## Step 4: Configure Pymakr

1. Open VSCode
2. Open the project folder containing the files
3. Edit the `pymakr.conf` file:
   - Update the "address" field with your COM port (e.g., "COM7" for Windows or "/dev/ttyUSB0" for Linux)

## Step 5: Upload Project Files

1. In VSCode, click on the Pymakr console at the bottom
2. Click "Upload" to upload all project files to the ESP32
3. Wait for the upload to complete

## Step 6: Run the Project

1. After uploading, the ESP32 will automatically run the code
2. If it doesn't start automatically, press the reset button on the ESP32
3. The display should show "Hello World" and attempt to connect to Wi-Fi

## Troubleshooting

### Connection Issues
- Make sure the correct COM port is selected in pymakr.conf
- Try a different USB cable
- Some USB ports may not provide enough power; try a different port

### Upload Failures
- Press the reset button on the ESP32 before uploading
- Some ESP32 boards require holding the BOOT button while pressing reset to enter download mode
- Try reducing the upload speed in pymakr.conf by setting "fast_upload" to false

### Display Issues
- Check all pin connections match those in the README.md file
- Ensure the ESP32 is receiving adequate power
- Try adjusting the display contrast if available

### Wi-Fi Connection Problems
- Verify the Wi-Fi network name and password in main.py
- Ensure the Wi-Fi network is within range
- Some networks may require additional authentication methods not supported by this code

## Additional Resources

- [MicroPython Documentation](https://docs.micropython.org/en/latest/)
- [ESP32 Technical Reference](https://www.espressif.com/en/support/documents/technical-documents)
- [Pymakr Documentation](https://marketplace.visualstudio.com/items?itemName=pycom.Pymakr)
