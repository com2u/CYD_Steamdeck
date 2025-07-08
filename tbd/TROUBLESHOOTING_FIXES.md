# ESP32 CYD PC Control System - Troubleshooting Fixes

## Recent Issues Fixed

### Issue 1: UART Initialization Error ✅
**Problem**: ESP32 showed UART error: `uart driver error` and `ESP_ERR_INVALID_STATE`

**Root Cause**: The code was trying to use UART 0, which is already used by the USB serial connection for debugging.

**Fix Applied**: 
- Changed UART from ID 0 to ID 2
- Updated pins to use GPIO 17 (TX) and GPIO 16 (RX)
- Updated in `main.py`: `init_serial_comm(uart_id=2, tx_pin=17, rx_pin=16)`

### Issue 2: Display Method Error ✅
**Problem**: ESP32 crashed with `AttributeError: 'Display' object has no attribute 'text'`

**Root Cause**: The ILI9341 Display class doesn't have a `text()` method, it has `draw_text8x8()`

**Fix Applied**:
- Changed `self.display_manager.clear_display()` to `self.display_manager.clear_screen()`
- Updated all text drawing from `self.display.text()` to `self.display.draw_text8x8()`
- Fixed button drawing to pass display object correctly
- Updated system info display methods to use correct text drawing

### Issue 3: Button Drawing Methods ✅
**Problem**: Button press/release methods were calling non-existent methods

**Root Cause**: Button class expects different method calls for visual feedback

**Fix Applied**:
- Changed `button.press()` to `button.set_pressed(True)` + `button.draw()`
- Changed `button.release()` to `button.set_pressed(False)` + `button.draw()`
- Updated touch detection to use `button.contains_point()` instead of `button.is_touched()`

### Issue 4: Audio Method Error ✅
**Problem**: ESP32 crashed with `AttributeError: 'AudioManager' object has no attribute 'play_beep'`

**Root Cause**: The AudioManager class has `play_button_click_tone()` method, not `play_beep()`

**Fix Applied**:
- Changed `self.audio_manager.play_beep()` to `self.audio_manager.play_button_click_tone()`

### Issue 5: Display Coordinate Errors ✅
**Problem**: ESP32 showing coordinate errors: "x-coordinate: 289 above maximum of 239"

**Root Cause**: Status text was positioned at x=200, but display width is only 240 pixels

**Fix Applied**:
- Moved status text from x=200 to x=180
- Shortened status text from "PC: Connected" to "Connected"

### Issue 6: System Data Not Updating ✅
**Problem**: ESP32 display showed all zeros for CPU, RAM, Network data

**Root Cause**: ESP32 UART 2 is not physically connected to PC, so no real data received

**Fix Applied**:
- Added demo data function `update_system_data_demo()` that shows current time and changing values
- This demonstrates the display is working while we work on real PC communication
- Demo data updates every 10 seconds with realistic changing values

### Issue 7: Display Layout Problems ✅
**Problem**: Exit button outside screen, status text unreadable, date/time too small

**Root Cause**: Button layout too wide, text positioning and sizing issues

**Fix Applied**:
- Reduced button width from 80px to 70px and spacing from 10px to 8px
- Changed status text from "Connected"/"Disconnected" to "OK"/"..." (shorter and clearer)
- Split date/time into two separate lines for better readability
- Moved status text position to fit properly on screen

### Issue 8: PC Command Communication ✅
**Problem**: ESP32 button presses not executing commands on PC

**Root Cause**: ESP32 sending commands via UART 2, but PC Service reading from USB

**Fix Applied**:
- Modified ESP32 to send commands via both UART 2 and USB debug output
- Added "PC_COMMAND:" prefix to debug output for PC Service to parse
- Updated PC Service to detect and execute commands from debug output
- Commands now work via USB connection without additional hardware

### Issue 9: Update Interval ✅
**Problem**: User requested 10-second update interval instead of 5 seconds

**Fix Applied**:
- Changed update interval from 5.0 seconds to 10.0 seconds in main loop
- System data and display now refresh every 10 seconds

## Hardware Connection for PC Communication

Since we're now using UART 2 for PC communication, you have two options:

### Option 1: USB Serial (Current Setup)
- ESP32 USB connection provides debugging output
- PC Service reads from the same USB port (COM7)
- UART 2 initialization will fail but system still works for display/buttons
- **This is the current working setup**

### Option 2: Separate Serial Connection (Future Enhancement)
If you want true bidirectional communication:
- Connect ESP32 GPIO 17 (TX) to PC serial adapter RX
- Connect ESP32 GPIO 16 (RX) to PC serial adapter TX
- Connect GND between ESP32 and PC serial adapter
- Update PC Service to use the new COM port

## Current System Status

✅ **Working Features**:
- ESP32 display shows buttons and interface
- Touch input works for button presses
- Audio feedback on button presses
- PC Service receives debug output from ESP32
- PC Service can execute commands (Init→Terminal, Test→Chrome, Exit→Shutdown)
- System monitoring and data collection on PC side

⚠️ **Partial Features**:
- ESP32→PC command sending (works via USB debug output)
- PC→ESP32 data sending (UART 2 not connected, but framework ready)

🔧 **To Enable Full Bidirectional Communication**:
1. Add external serial connection (GPIO 17/16 to PC serial adapter)
2. Update PC Service to use the new serial port
3. System will then show real-time PC data on ESP32 display

## Testing the Current System

1. **Upload ESP32 Code**: Run `upload.bat` to upload all files
2. **Start PC Service**: Run `PC_Service/start_service.bat`
3. **Test Buttons**: Touch buttons on ESP32 display
4. **Check PC Service**: Commands should execute on PC
5. **Monitor Debug**: PC Service shows ESP32 debug output

## Files Updated in This Fix

- `main.py` - Fixed UART, display, and button methods
- `upload.bat` - Added new communication files
- `upload.sh` - Added new communication files
- `TROUBLESHOOTING_FIXES.md` - This documentation

## Next Steps for Full Communication

If you want to enable the full bidirectional communication with real-time system data on the ESP32 display:

1. **Hardware**: Connect ESP32 GPIO 17/16 to a USB-to-Serial adapter
2. **PC Service**: Update the COM port in the PC service to use the new adapter
3. **Testing**: The ESP32 will then show live CPU, RAM, and network data from your PC

The system is now stable and working with the current USB connection setup!
