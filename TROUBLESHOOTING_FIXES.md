# ESP32 CYD PC Control System - Troubleshooting Fixes

## Recent Issues Fixed

### Issue 1: UART Initialization Error
**Problem**: ESP32 showed UART error: `uart driver error` and `ESP_ERR_INVALID_STATE`

**Root Cause**: The code was trying to use UART 0, which is already used by the USB serial connection for debugging.

**Fix Applied**: 
- Changed UART from ID 0 to ID 2
- Updated pins to use GPIO 17 (TX) and GPIO 16 (RX)
- Updated in `main.py`: `init_serial_comm(uart_id=2, tx_pin=17, rx_pin=16)`

### Issue 2: Display Method Error
**Problem**: ESP32 crashed with `AttributeError: 'DisplayManager' object has no attribute 'clear_display'`

**Root Cause**: The DisplayManager class has `clear_screen()` method, not `clear_display()`

**Fix Applied**:
- Changed `self.display_manager.clear_display()` to `self.display_manager.clear_screen()`
- Updated all text drawing to use `self.display.text()` directly
- Fixed button drawing to pass display object correctly

### Issue 3: Button Drawing Methods
**Problem**: Button press/release methods were calling non-existent methods

**Root Cause**: Button class expects different method calls for visual feedback

**Fix Applied**:
- Changed `button.press()` to `button.set_pressed(True)` + `button.draw()`
- Changed `button.release()` to `button.set_pressed(False)` + `button.draw()`
- Updated touch detection to use `button.contains_point()` instead of `button.is_touched()`

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
