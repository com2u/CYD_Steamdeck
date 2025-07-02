@echo off
echo ===================================
echo ESP32-2432S028R MicroPython Uploader
echo ===================================
echo.

REM Set the COM port (change if needed)
set PORT=COM7

echo Installing mpremote...
pip install mpremote
if %ERRORLEVEL% NEQ 0 (
    echo Failed to install mpremote. Please install it manually with:
    echo pip install mpremote
    pause
    exit /b 1
)

echo.
echo Uploading files to ESP32 on %PORT%...
echo.

echo 1/6 Uploading boot.py...
python -m mpremote connect %PORT% cp boot.py :boot.py
if %ERRORLEVEL% NEQ 0 (
    echo Failed to upload boot.py
    goto error
)

echo 2/6 Uploading ili9341.py...
python -m mpremote connect %PORT% cp ili9341.py :ili9341.py
if %ERRORLEVEL% NEQ 0 (
    echo Failed to upload ili9341.py
    goto error
)

echo 3/6 Uploading xpt2046.py...
python -m mpremote connect %PORT% cp xpt2046.py :xpt2046.py
if %ERRORLEVEL% NEQ 0 (
    echo Failed to upload xpt2046.py
    goto error
)

echo 4/8 Uploading test.py...
python -m mpremote connect %PORT% cp test.py :test.py
if %errorlevel% neq 0 (
    echo Failed to upload test.py
    set ERROR=1
)

echo 5/8 Uploading button.py...
python -m mpremote connect %PORT% cp button.py :button.py
if %errorlevel% neq 0 (
    echo Failed to upload button.py
    set ERROR=1
)

echo 6/8 Uploading display.py...
python -m mpremote connect %PORT% cp display.py :display.py
if %errorlevel% neq 0 (
    echo Failed to upload display.py
    set ERROR=1
)

echo 7/11 Uploading commands.py...
python -m mpremote connect %PORT% cp commands.py :commands.py
if %errorlevel% neq 0 (
    echo Failed to upload commands.py
    set ERROR=1
)

echo 8/11 Uploading audio.py...
python -m mpremote connect %PORT% cp audio.py :audio.py
if %errorlevel% neq 0 (
    echo Failed to upload audio.py
    set ERROR=1
)

echo 9/11 Uploading json_protocol.py...
python -m mpremote connect %PORT% cp json_protocol.py :json_protocol.py
if %errorlevel% neq 0 (
    echo Failed to upload json_protocol.py
    set ERROR=1
)

echo 10/11 Uploading serial_comm.py...
python -m mpremote connect %PORT% cp serial_comm.py :serial_comm.py
if %errorlevel% neq 0 (
    echo Failed to upload serial_comm.py
    set ERROR=1
)

echo 11/11 Uploading main.py...
python -m mpremote connect %PORT% cp main.py :main.py
if %ERRORLEVEL% NEQ 0 (
    echo Failed to upload main.py
    goto error
)

echo.
echo Verifying files on ESP32...
python -m mpremote connect %PORT% ls
if %ERRORLEVEL% NEQ 0 (
    echo Failed to list files
    goto error
)

echo.
echo Upload complete!
echo.
echo Resetting ESP32...
python -m mpremote connect %PORT% reset
if %ERRORLEVEL% NEQ 0 (
    echo Failed to reset ESP32. Please press the reset button on the device.
)

echo.
echo ===================================
echo All files uploaded successfully!
echo.
echo The ESP32 should now boot with the button interface.
echo After power cycle, main.py should run automatically.
echo ===================================
goto end

:error
echo.
echo ===================================
echo Error occurred during upload!
echo.
echo Troubleshooting tips:
echo - Make sure the ESP32 is connected to %PORT%
echo - Check that no other program is using the port
echo - Try pressing the reset button on the ESP32
echo - Some ESP32 boards require holding the BOOT button while pressing reset
echo ===================================

:end
