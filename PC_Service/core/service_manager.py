"""
Service Manager for ESP32 CYD PC Service
Main orchestration and lifecycle management
"""
import time
import threading
from typing import Dict, Any, Optional
from core.json_protocol import (
    parse_message, create_system_data_message, create_status_message,
    create_ack_message, MessageType, CommandType, StatusType
)
from core.serial_handler import SerialHandler
from core.system_monitor import get_system_data, get_formatted_summary
from commands.terminal_commands import open_terminal
from commands.browser_commands import open_chrome
from commands.system_commands import shutdown
from config import SYSTEM_UPDATE_INTERVAL, SERVICE_NAME, VERSION


class ServiceManager:
    """Main service manager that coordinates all components"""
    
    def __init__(self, port: str):
        self.port = port
        self.running = False
        self.serial_handler: Optional[SerialHandler] = None
        self.system_update_thread: Optional[threading.Thread] = None
        self.last_system_update = 0
        
        # Statistics
        self.start_time = None
        self.commands_processed = 0
        self.last_command_time = None
        
        print(f"=== {SERVICE_NAME} v{VERSION} ===")
        print(f"Initializing service for port: {port}")
    
    def start(self) -> bool:
        """Start the service"""
        if self.running:
            print("Service is already running")
            return True
        
        print("Starting ESP32 CYD PC Service...")
        self.running = True
        self.start_time = time.time()
        
        # Initialize serial handler
        self.serial_handler = SerialHandler(
            port=self.port,
            on_message_received=self._handle_received_message,
            on_connection_changed=self._handle_connection_changed
        )
        
        # Start serial communication
        if not self.serial_handler.start():
            print(f"Failed to start serial handler on {self.port}")
            print("Service will continue trying to connect...")
        
        # Start system monitoring thread
        self.system_update_thread = threading.Thread(
            target=self._system_update_loop, 
            daemon=True
        )
        self.system_update_thread.start()
        
        print("Service started successfully!")
        print("Waiting for ESP32 connection...")
        return True
    
    def stop(self):
        """Stop the service"""
        if not self.running:
            return
        
        print("Stopping ESP32 CYD PC Service...")
        self.running = False
        
        # Stop serial handler
        if self.serial_handler:
            self.serial_handler.stop()
        
        # Wait for system update thread to finish
        if self.system_update_thread and self.system_update_thread.is_alive():
            self.system_update_thread.join(timeout=2.0)
        
        print("Service stopped")
    
    def _handle_received_message(self, raw_message: str):
        """Handle messages received from ESP32"""
        # Check for PC_COMMAND: prefix in debug output
        if raw_message.startswith("PC_COMMAND:"):
            command = raw_message.split("PC_COMMAND:")[1].strip()
            print(f"Received command from ESP32 debug: {command}")
            
            # Create a command message and handle it
            command_message = {
                "type": "command",
                "action": command,
                "timestamp": time.time()
            }
            self._handle_command_message(command_message)
            return
        
        # Try to parse as JSON
        message = parse_message(raw_message)
        
        if message:
            # Valid JSON message
            self._handle_json_message(message)
        else:
            # Not JSON, treat as debug output
            print(f"ESP32 Debug: {raw_message}")
    
    def _handle_json_message(self, message: Dict[str, Any]):
        """Handle parsed JSON messages from ESP32"""
        message_type = message.get("type")
        
        if message_type == MessageType.COMMAND:
            self._handle_command_message(message)
        elif message_type == MessageType.HEARTBEAT:
            self._handle_heartbeat_message(message)
        else:
            print(f"Unknown message type: {message_type}")
    
    def _handle_command_message(self, message: Dict[str, Any]):
        """Handle command messages from ESP32"""
        try:
            action = message.get("action")
            timestamp = message.get("timestamp", time.time())
            
            print(f"Received command: {action}")
            self.commands_processed += 1
            self.last_command_time = time.time()
            
            # Execute the command
            result = self._execute_command(action)
            
            # Send acknowledgment
            ack_message = create_ack_message(
                action, 
                "success" if result.success else "failed",
                result.message
            )
            
            if self.serial_handler:
                self.serial_handler.send_message(ack_message)
            
            print(f"Command {action} result: {result.message}")
            
        except Exception as e:
            print(f"Error handling command message: {e}")
            # Send error acknowledgment
            if self.serial_handler:
                error_ack = create_ack_message(
                    message.get("action", "unknown"),
                    "error",
                    f"Error processing command: {str(e)}"
                )
                self.serial_handler.send_message(error_ack)
    
    def _handle_heartbeat_message(self, message: Dict[str, Any]):
        """Handle heartbeat messages from ESP32"""
        timestamp = message.get("timestamp", time.time())
        print(f"Heartbeat received from ESP32 (timestamp: {timestamp})")
    
    def _execute_command(self, action: str):
        """Execute a command based on the action"""
        if action == CommandType.INIT:
            return open_terminal()
        elif action == CommandType.TEST:
            return open_chrome()
        elif action == CommandType.EXIT:
            return shutdown()
        else:
            from commands.command_executor import CommandResult
            return CommandResult(False, f"Unknown command: {action}")
    
    def _handle_connection_changed(self, connected: bool):
        """Handle serial connection state changes"""
        if connected:
            print("ESP32 connected!")
            # Send connection status
            status_message = create_status_message(StatusType.CONNECTED)
            if self.serial_handler:
                self.serial_handler.send_message(status_message)
        else:
            print("ESP32 disconnected!")
    
    def _system_update_loop(self):
        """Background thread that sends system updates to ESP32"""
        while self.running:
            try:
                current_time = time.time()
                
                # Check if it's time to send system update
                if current_time - self.last_system_update >= SYSTEM_UPDATE_INTERVAL:
                    self._send_system_update()
                    self.last_system_update = current_time
                
                # Sleep for a short time to prevent busy waiting
                time.sleep(1.0)
                
            except Exception as e:
                print(f"Error in system update loop: {e}")
                time.sleep(5.0)  # Wait longer on error
    
    def _send_system_update(self):
        """Send system information to ESP32"""
        try:
            # Get system data
            system_data = get_system_data()
            
            # Create system data message
            message = create_system_data_message(system_data)
            
            # Send via serial connection (this goes to ESP32's USB serial)
            if self.serial_handler and self.serial_handler.is_connected:
                # Send the JSON message directly
                self.serial_handler.send_message(message)
                # Also send a debug marker that ESP32 can parse
                self.serial_handler.send_message(f"ESP32_DATA:{message.strip()}")
                print("System data sent to ESP32 via serial")
            else:
                print("No serial connection - system data not sent")
            
            # ALSO send via debug output that ESP32 can see
            print(f"PC_SYSTEM_DATA:{message.strip()}")
            
            # Log summary
            summary = get_formatted_summary()
            print(f"System update sent: {summary}")
            
        except Exception as e:
            print(f"Error sending system update: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get service status information"""
        uptime = time.time() - self.start_time if self.start_time else 0
        
        status = {
            "service_name": SERVICE_NAME,
            "version": VERSION,
            "running": self.running,
            "uptime_seconds": uptime,
            "port": self.port,
            "commands_processed": self.commands_processed,
            "last_command_time": self.last_command_time,
            "last_system_update": self.last_system_update
        }
        
        # Add serial handler status
        if self.serial_handler:
            status["serial"] = self.serial_handler.get_status()
        
        return status
    
    def send_test_message(self):
        """Send a test message to ESP32 (for debugging)"""
        if self.serial_handler:
            test_message = create_status_message(StatusType.READY, "Test message from PC")
            self.serial_handler.send_message(test_message)
            print("Test message sent to ESP32")
        else:
            print("No serial handler available")
    
    def force_system_update(self):
        """Force an immediate system update"""
        self._send_system_update()
        print("System update sent immediately")
    
    def change_port(self, new_port: str) -> bool:
        """Change the serial port"""
        if self.serial_handler:
            success = self.serial_handler.change_port(new_port)
            if success:
                self.port = new_port
                print(f"Port changed to {new_port}")
            return success
        return False


def create_service_manager(port: str) -> ServiceManager:
    """Factory function to create a service manager"""
    return ServiceManager(port)
