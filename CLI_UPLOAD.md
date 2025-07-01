# Uploading MicroPython Project via Command Line

If you prefer using the command line instead of the VSCode Pymakr extension, you can use tools like `mpremote`, `rshell`, or other utilities to upload files to your ESP32. Here's how to do it:

## Option 1: Using mpremote (Recommended)

### Step 1: Install mpremote

```
pip install mpremote
```

### Step 2: Upload Files

Upload each file individually to the ESP32. Replace `COM7` with your port if different:

```bash
# Upload boot.py
python -m mpremote connect COM7 cp boot.py :boot.py

# Upload main.py
python -m mpremote connect COM7 cp main.py :main.py

# Upload ili9341.py
python -m mpremote connect COM7 cp ili9341.py :ili9341.py

# Upload xpt2046.py
python -m mpremote connect COM7 cp xpt2046.py :xpt2046.py

# Upload test.py (optional)
python -m mpremote connect COM7 cp test.py :test.py
```

You can also upload multiple files in one command:

```bash
python -m mpremote connect COM7 cp boot.py main.py ili9341.py xpt2046.py test.py :
```

### Step 3: Verify Files

List files on the ESP32 to verify they were uploaded:

```bash
python -m mpremote connect COM7 ls
```

### Step 4: Reset the ESP32

Either press the reset button on the ESP32 or use:

```bash
python -m mpremote connect COM7 reset
```

## Option 2: Using Rshell

### Step 1: Install Rshell

```
pip install rshell
```

### Step 2: Connect to the ESP32

```bash
rshell -p COM7
```

### Step 3: Upload Files

Once in the rshell environment, you can copy files to the ESP32:

```bash
# Inside rshell
cp boot.py /pyboard/
cp main.py /pyboard/
cp ili9341.py /pyboard/
cp xpt2046.py /pyboard/
cp test.py /pyboard/
```

Alternatively, you can use the `rsync` command to upload all files at once:

```bash
# Inside rshell
rsync . /pyboard
```

### Step 4: Verify Files

List files on the ESP32:

```bash
# Inside rshell
ls /pyboard
```

### Step 5: Reset and Exit

```bash
# Inside rshell
repl
# Press Ctrl+D to soft reset the ESP32
# Press Ctrl+X to exit REPL
exit
```

## Option 3: Using mpfshell

### Step 1: Install mpfshell

```
pip install mpfshell
```

### Step 2: Connect and Upload

```bash
# Start mpfshell
mpfshell

# Connect to ESP32 (inside mpfshell)
open COM7

# Upload files (inside mpfshell)
put boot.py
put main.py
put ili9341.py
put xpt2046.py
put test.py

# List files to verify
ls

# Reset ESP32
reset

# Exit mpfshell
exit
```

## Batch Script for Windows

We've provided a batch file (upload.bat) to automate the upload process using mpremote:

```batch
@echo off
echo Uploading files to ESP32...
python -m mpremote connect COM7 cp boot.py :boot.py
python -m mpremote connect COM7 cp main.py :main.py
python -m mpremote connect COM7 cp ili9341.py :ili9341.py
python -m mpremote connect COM7 cp xpt2046.py :xpt2046.py
python -m mpremote connect COM7 cp test.py :test.py
echo Upload complete!
echo Resetting ESP32...
python -m mpremote connect COM7 reset
echo Done!
```

## Shell Script for macOS/Linux

We've provided a shell script (upload.sh) to automate the upload process using mpremote:

```bash
#!/bin/bash
echo "Uploading files to ESP32..."
python -m mpremote connect /dev/ttyUSB0 cp boot.py :boot.py
python -m mpremote connect /dev/ttyUSB0 cp main.py :main.py
python -m mpremote connect /dev/ttyUSB0 cp ili9341.py :ili9341.py
python -m mpremote connect /dev/ttyUSB0 cp xpt2046.py :xpt2046.py
python -m mpremote connect /dev/ttyUSB0 cp test.py :test.py
echo "Upload complete!"
echo "Resetting ESP32..."
python -m mpremote connect /dev/ttyUSB0 reset
echo "Done!"
```

Make the script executable:

```bash
chmod +x upload.sh
```

## Troubleshooting CLI Upload Issues

### Port Access Permission Issues (Linux/macOS)

If you get permission errors on Linux or macOS:

```bash
sudo chmod 666 /dev/ttyUSB0  # Replace with your port
```

### Connection Errors

- Make sure no other program (like Pymakr or Serial Monitor) is using the port
- Try pressing the reset button on the ESP32 before uploading
- Some ESP32 boards require holding the BOOT button while pressing reset to enter download mode

### Timeout Errors

- Try reconnecting the ESP32
- Check if the ESP32 is in a bootloop (check the serial output)
- Make sure the ESP32 has MicroPython firmware installed

### File Not Found Errors

- Make sure you're in the correct directory containing the files
- Check file names for typos
