# ESP32-PC Communication System Setup Guide

This guide will help you set up the bidirectional communication system between your ESP32 display and PC.

## Overview

The system consists of:
- **ESP32 Side**: Modified firmware with serial communication and system data display
- **PC Side**: Python service that monitors system resources and executes commands

## Features

### ESP32 Display Features
- **3 Command Buttons**: Init, Test, Exit
- **Real-time System Info Display**:
  - Connection status (CONN/DISC)
  - Current date and time
  - CPU usage percentage
  - RAM usage (percentage and GB)
  - Network transfer rates (TX/RX)

### PC Service Features
- **Command Execution**:
  - `Init` → Opens Windows Terminal
  - `Test` → Launches Chrome browser
  - `Exit` → Schedules system shutdown (60-second delay with cancel option)
- **System Monitoring**: Real-time data collection and transmission to ESP32
- **Auto-discovery**: Attempts to find ESP32 serial port automatically

## Setup Instructions

### 1. PC Service Setup

#### Install Python Dependencies
```bash
cd PC_Service
pip install -r requirements.txt
```

The required packages are:
- `pyserial>=3.5` - Serial communication
- `psutil>=5.9.0` - System monitoring

#### Run the PC Service
```bash
cd PC_Service
python pc_service.py
```

The service will:
1. Try to automatically detect your ESP32's serial port
2. If not found, prompt you to enter the port manually (e.g., COM3)
3. Start listening for ESP32 commands
4. Begin sending system data to ESP32

### 2. ESP32 Setup

#### Upload New Firmware
1. Upload all the new/modified files to your ESP32:
   - `serial_comm.py` (new)
   - `commands.py` (modified)
   - `button.py` (modified)
   - `main.py` (modified)

2. The ESP32 will now display:
   - 3 buttons on the left side (Init, Test, Exit)
   - System information on the right side

#### Connect ESP32 to PC
1. Connect ESP32 to PC via USB cable
2. Note the COM port (e.g., COM3, COM4)
3. Make sure no other serial monitors are using the port

## Usage

### Starting the System

1. **Start PC Service First**:
   ```bash
   cd PC_Service
   python pc_service.py
   ```

2. **Reset or Power On ESP32**: The ESP32 will automatically start communicating with the PC service

3. **Verify Connection**: Look for "CONN" status on the ESP32 display

### Using the Commands

#### Init Button
- **Action**: Opens Windows Terminal
- **ESP32 Display**: Shows command being sent
- **PC Response**: Terminal window opens

#### Test Button
- **Action**: Launches Chrome browser
- **ESP32 Display**: Shows command being sent
- **PC Response**: Chrome browser starts

#### Exit Button
- **Action**: Schedules system shutdown
- **ESP32 Display**: Shows command being sent
- **PC Response**: 
  - System shutdown scheduled in 60 seconds
  - Message displayed with cancel instructions
  - Run `shutdown /a` in command prompt to cancel

### System Information Display

The right side of the ESP32 display shows:
- **CONN/DISC**: Connection status with PC
- **Date**: Current date (YYYY-MM-DD)
- **Time**: Current time (HH:MM:SS)
- **CPU**: CPU usage percentage
- **RAM**: RAM usage percentage and GB used/total
- **TX/RX**: Network transfer rates

## Troubleshooting

### ESP32 Shows "DISC" (Disconnected)
1. Check USB cable connection
2. Verify PC service is running
3. Ensure correct COM port is being used
4. Check that no other programs are using the serial port

### PC Service Can't Find ESP32
1. Check Device Manager for COM ports
2. Look for "USB Serial Device" or similar
3. Manually specify the port when prompted
4. Try different USB cables/ports

### Commands Not Working
1. Verify ESP32 shows "CONN" status
2. Check PC service console for error messages
3. Ensure ESP32 is sending commands (check serial output)

### System Data Not Updating
1. Check PC service is running and connected
2. Verify psutil is installed correctly
3. Look for error messages in PC service console

## Customization

### Adding New Commands
1. **ESP32 Side**: Add new button in `commands.py`
2. **PC Side**: Add new command handler in `CommandExecutor` class

### Changing Update Intervals
- **ESP32**: Modify intervals in `main.py`
- **PC**: Modify sleep intervals in `pc_service.py`

### Modifying Display Layout
- Edit `draw_system_info()` method in `commands.py`
- Adjust button layout in `create_button_interface()`

## Technical Details

### Communication Protocol
- **Format**: JSON messages over serial
- **Baud Rate**: 115200
- **Message Types**:
  - `command`: ESP32 to PC
  - `system_data`: PC to ESP32
  - `heartbeat`: Keep-alive messages

### Serial Configuration
- **ESP32**: UART0 (USB serial)
- **PC**: Auto-detected or manually specified COM port
- **Settings**: 115200 baud, 8N1

### Error Handling
- Automatic reconnection attempts
- JSON parsing error recovery
- Timeout handling for stale data

## Safety Notes

⚠️ **Important**: The Exit command will shutdown your PC! Make sure to:
- Save all work before testing
- Remember you can cancel with `shutdown /a`
- Consider modifying the shutdown delay if needed

## Support

If you encounter issues:
1. Check the console output from both ESP32 and PC service
2. Verify all dependencies are installed
3. Ensure proper wiring and connections
4. Test with a simple serial terminal first
