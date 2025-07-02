# ESP32 CYD PC Control System

A comprehensive system that turns your ESP32 Cheap Yellow Display (CYD) into a remote control for your PC, with bidirectional communication showing real-time system information.

## Features

### ESP32 Display Side
- **Touch Interface**: 3 customizable buttons (Init, Test, Exit)
- **Real-time System Info**: Shows PC date/time, CPU usage, RAM usage, and network statistics
- **Visual Feedback**: Button press animations and connection status indicators
- **Audio Feedback**: Beep sounds for button presses and system events
- **Robust Communication**: Automatic reconnection and error handling
- **Independent Operation**: Works without WiFi, purely USB serial communication

### PC Service Side
- **Command Execution**: 
  - Init → Opens Terminal/Command Prompt
  - Test → Opens Chrome browser
  - Exit → Initiates system shutdown (with optional confirmation)
- **System Monitoring**: Real-time CPU, RAM, and network usage
- **Robust Serial Communication**: Automatic reconnection and error recovery
- **Interactive Console**: Status monitoring and debugging commands
- **Cross-Platform**: Works on Windows, macOS, and Linux

## Hardware Requirements

- ESP32-2432S028R (Cheap Yellow Display)
- USB cable for ESP32 connection
- PC with Python 3.7+ and available serial port

## Quick Start

### 1. ESP32 Setup

1. **Upload ESP32 Code**:
   ```bash
   # Copy all .py files to your ESP32
   # Use Thonny, ampy, or your preferred method
   ```

2. **Required Files on ESP32**:
   - `main.py` - Main application
   - `display.py` - Display management
   - `button.py` - Button handling
   - `audio.py` - Audio feedback
   - `serial_comm.py` - Serial communication
   - `json_protocol.py` - Message protocol
   - `ili9341.py` - Display driver
   - `xpt2046.py` - Touch driver (if using)

### 2. PC Service Setup

1. **Install Python Dependencies**:
   ```bash
   cd PC_Service
   # Option 1: Use the installer
   install.bat
   
   # Option 2: Manual installation
   pip install -r requirements.txt
   ```

2. **Start the Service**:
   ```bash
   # Option 1: Use the batch file (Windows)
   start_service.bat
   
   # Option 2: Manual start
   python main.py --port COM7
   ```

3. **Check Connection**:
   - The ESP32 should show "PC: Connected" when the service is running
   - The PC service will show connection status and debug output

## System Architecture

```
ESP32 CYD                    PC Service
┌─────────────────┐         ┌─────────────────┐
│  Touch Interface│◄────────┤  Command Handler│
│  ┌─────┬─────┬──┴┐        │  ┌─────────────┐│
│  │Init │Test │Exit│        │  │Terminal     ││
│  └─────┴─────┴────┘        │  │Browser      ││
│  System Info Display       │  │System Ops   ││
│  ┌─────────────────┐       │  └─────────────┘│
│  │Date: 2025-01-02 │       │                 │
│  │Time: 14:30:15   │       │  System Monitor │
│  │CPU: 25.3%       │◄──────┤  ┌─────────────┐│
│  │RAM: 8.2/16.0 GB │       │  │CPU Usage    ││
│  │NET: U:1.2 D:5.8 │       │  │RAM Usage    ││
│  └─────────────────┘       │  │Network I/O  ││
│                             │  └─────────────┘│
│  Serial Communication      │                 │
│  ┌─────────────────┐       │  Serial Handler │
│  │JSON Protocol    │◄──────┤  ┌─────────────┐│
│  │Auto Reconnect   │  USB  │  │Robust Comm  ││
│  │Error Handling   │◄──────┤  │Auto Reconnect││
│  └─────────────────┘       │  │Message Queue││
└─────────────────────────────┤  └─────────────┘│
                              └─────────────────┘
```

## Communication Protocol

The system uses a JSON-based protocol over USB serial:

### Message Types

1. **Commands** (ESP32 → PC):
   ```json
   {
     "type": "command",
     "action": "INIT|TEST|EXIT",
     "timestamp": 1704196815.123
   }
   ```

2. **System Data** (PC → ESP32):
   ```json
   {
     "type": "system_data",
     "timestamp": 1704196815.123,
     "data": {
       "date": "2025-01-02",
       "time": "14:30:15",
       "cpu_percent": 25.3,
       "ram_used_gb": 8.2,
       "ram_total_gb": 16.0,
       "network_sent_mb": 1234.5,
       "network_recv_mb": 5678.9
     }
   }
   ```

3. **Acknowledgments** (PC → ESP32):
   ```json
   {
     "type": "ack",
     "command": "INIT",
     "result": "success|failed",
     "message": "Terminal opened successfully",
     "timestamp": 1704196815.123
   }
   ```

## Configuration

### PC Service Configuration

Edit `PC_Service/config.py`:

```python
# Serial Communication
DEFAULT_SERIAL_PORT = "COM7"  # Change to your port
BAUD_RATE = 115200
SERIAL_TIMEOUT = 1.0

# System Monitoring
SYSTEM_UPDATE_INTERVAL = 10.0  # seconds
CPU_SAMPLE_INTERVAL = 0.1

# Security
REQUIRE_SHUTDOWN_CONFIRMATION = True
SHUTDOWN_CONFIRMATION_TIMEOUT = 10.0
```

### ESP32 Configuration

The ESP32 code automatically detects hardware and initializes appropriately. No configuration needed for basic operation.

## Troubleshooting

### Common Issues

1. **ESP32 Not Connecting**:
   - Check USB cable and port
   - Verify correct COM port in PC service
   - Try different USB port
   - Check ESP32 power and reset

2. **PC Service Won't Start**:
   - Install Python dependencies: `pip install pyserial psutil`
   - Check Python version (3.7+ required)
   - Verify serial port permissions

3. **Commands Not Working**:
   - Check serial connection status
   - Verify JSON protocol messages in debug output
   - Test with interactive commands in PC service

4. **System Info Not Updating**:
   - Check PC service is sending data (every 10 seconds)
   - Verify ESP32 is receiving JSON messages
   - Check for serial communication errors

### Debug Commands

PC Service interactive commands:
- `status` - Show service status
- `test` - Send test message to ESP32
- `update` - Force system update
- `port` - Change serial port
- `help` - Show all commands

### Log Analysis

Both ESP32 and PC service provide detailed logging:
- ESP32: Serial output shows connection status and received data
- PC Service: Console shows command execution and system monitoring

## File Structure

```
ESP32_CYD_Project/
├── ESP32 Files (upload to ESP32):
│   ├── main.py              # Main application
│   ├── display.py           # Display management
│   ├── button.py            # Button handling
│   ├── audio.py             # Audio feedback
│   ├── serial_comm.py       # Serial communication
│   ├── json_protocol.py     # Message protocol
│   ├── ili9341.py           # Display driver
│   └── xpt2046.py           # Touch driver
│
├── PC_Service/              # PC Service
│   ├── main.py              # Service entry point
│   ├── config.py            # Configuration
│   ├── requirements.txt     # Python dependencies
│   ├── install.bat          # Installation script
│   ├── start_service.bat    # Startup script
│   │
│   ├── core/                # Core modules
│   │   ├── service_manager.py
│   │   ├── serial_handler.py
│   │   ├── system_monitor.py
│   │   └── json_protocol.py
│   │
│   └── commands/            # Command modules
│       ├── command_executor.py
│       ├── terminal_commands.py
│       ├── browser_commands.py
│       └── system_commands.py
│
└── Documentation:
    ├── README.md            # This file
    ├── UPLOAD_INSTRUCTIONS.md
    └── CLI_UPLOAD.md
```

## Advanced Usage

### Custom Commands

Add new commands by:

1. **ESP32 Side**: Add button in `main.py`
2. **PC Side**: Add command handler in `PC_Service/core/service_manager.py`
3. **Protocol**: Update command types in both `json_protocol.py` files

### System Integration

The PC service can be:
- Run as a Windows service
- Started automatically on boot
- Integrated with system monitoring tools
- Extended with additional hardware control

### Security Considerations

- Shutdown commands can require confirmation
- Serial communication is local only (no network exposure)
- Commands are validated before execution
- Error handling prevents system crashes

## License

This project is open source. Feel free to modify and distribute according to your needs.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review debug output from both ESP32 and PC
3. Verify hardware connections and software installation
4. Test with minimal configuration first

## Version History

- **v1.0**: Initial release with basic button control
- **v2.0**: Added system monitoring and JSON protocol
- **v2.1**: Enhanced error handling and reconnection
- **v2.2**: Added audio feedback and visual improvements
