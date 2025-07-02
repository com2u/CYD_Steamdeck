"""
Serial Communication module for ESP32 CYD
Handles UART communication with PC with robust reconnection
"""
import time
from machine import UART
from json_protocol import parse_message, is_json_line


class SerialComm:
    """Handles serial communication with PC"""
    
    def __init__(self, uart_id=0, baudrate=115200, tx_pin=1, rx_pin=3):
        self.uart_id = uart_id
        self.baudrate = baudrate
        self.tx_pin = tx_pin
        self.rx_pin = rx_pin
        self.uart = None
        self.is_connected = False
        self.last_connection_attempt = 0
        self.connection_retry_delay = 2.0  # seconds
        
        # Message handling
        self.on_message_received = None
        self.on_connection_changed = None
        
        # Statistics
        self.messages_sent = 0
        self.messages_received = 0
        self.connection_attempts = 0
        
        # Buffer for incomplete messages
        self.receive_buffer = ""
        
        print("SerialComm initialized")
    
    def init_uart(self) -> bool:
        """Initialize UART connection"""
        try:
            print(f"Initializing UART {self.uart_id} at {self.baudrate} baud...")
            self.connection_attempts += 1
            
            # Initialize UART
            self.uart = UART(self.uart_id, baudrate=self.baudrate, tx=self.tx_pin, rx=self.rx_pin)
            
            if self.uart:
                self.is_connected = True
                print("UART initialized successfully")
                
                # Notify connection change
                if self.on_connection_changed:
                    self.on_connection_changed(True)
                
                return True
            else:
                print("Failed to initialize UART")
                return False
                
        except Exception as e:
            print(f"UART initialization error: {e}")
            return False
    
    def deinit_uart(self):
        """Deinitialize UART connection"""
        if self.uart:
            try:
                self.uart.deinit()
                print("UART deinitialized")
            except Exception as e:
                print(f"Error deinitializing UART: {e}")
            finally:
                self.uart = None
        
        if self.is_connected:
            self.is_connected = False
            # Notify connection change
            if self.on_connection_changed:
                self.on_connection_changed(False)
    
    def send_message(self, message: str) -> bool:
        """Send a message to PC"""
        if not self.is_connected or not self.uart:
            print("Cannot send message: UART not connected")
            return False
        
        try:
            # Ensure message ends with newline
            if not message.endswith('\n'):
                message += '\n'
            
            # Send message
            bytes_written = self.uart.write(message.encode('utf-8'))
            
            if bytes_written:
                self.messages_sent += 1
                print(f"Sent: {message.strip()}")
                return True
            else:
                print("Failed to send message")
                return False
                
        except Exception as e:
            print(f"Error sending message: {e}")
            self._handle_connection_error()
            return False
    
    def check_for_messages(self):
        """Check for incoming messages from PC"""
        if not self.is_connected or not self.uart:
            return
        
        try:
            # Check if data is available
            if self.uart.any():
                # Read available data
                data = self.uart.read()
                if data:
                    # Decode and add to buffer
                    text = data.decode('utf-8', errors='ignore')
                    self.receive_buffer += text
                    
                    # Process complete lines
                    self._process_receive_buffer()
                    
        except Exception as e:
            print(f"Error reading from UART: {e}")
            self._handle_connection_error()
    
    def _process_receive_buffer(self):
        """Process the receive buffer for complete messages"""
        while '\n' in self.receive_buffer:
            # Extract one complete line
            line, self.receive_buffer = self.receive_buffer.split('\n', 1)
            line = line.strip()
            
            if line:
                self.messages_received += 1
                self._handle_received_message(line)
    
    def _handle_received_message(self, message: str):
        """Handle a received message"""
        # Try to parse as JSON first
        parsed_message = parse_message(message)
        
        if parsed_message:
            # Valid JSON message
            print(f"JSON received: {message}")
            if self.on_message_received:
                self.on_message_received(parsed_message, True)  # True = is_json
        else:
            # Not JSON, treat as debug/status message
            print(f"PC Debug: {message}")
            if self.on_message_received:
                self.on_message_received(message, False)  # False = not_json
    
    def _handle_connection_error(self):
        """Handle connection errors"""
        print("Connection error detected, marking as disconnected")
        self.deinit_uart()
    
    def try_reconnect(self) -> bool:
        """Try to reconnect if not connected"""
        current_time = time.time()
        
        # Check if enough time has passed since last attempt
        if current_time - self.last_connection_attempt < self.connection_retry_delay:
            return False
        
        self.last_connection_attempt = current_time
        
        if not self.is_connected:
            print("Attempting to reconnect UART...")
            return self.init_uart()
        
        return True
    
    def get_status(self) -> dict:
        """Get connection status and statistics"""
        return {
            "connected": self.is_connected,
            "uart_id": self.uart_id,
            "baudrate": self.baudrate,
            "messages_sent": self.messages_sent,
            "messages_received": self.messages_received,
            "connection_attempts": self.connection_attempts,
            "buffer_length": len(self.receive_buffer)
        }
    
    def set_message_callback(self, callback):
        """Set callback for received messages"""
        self.on_message_received = callback
    
    def set_connection_callback(self, callback):
        """Set callback for connection state changes"""
        self.on_connection_changed = callback
    
    def send_heartbeat(self) -> bool:
        """Send a heartbeat message"""
        try:
            from json_protocol import create_heartbeat_message
            heartbeat = create_heartbeat_message()
            return self.send_message(heartbeat)
        except Exception as e:
            print(f"Error sending heartbeat: {e}")
            return False
    
    def send_command(self, action: str) -> bool:
        """Send a command message"""
        from json_protocol import create_command_message
        command = create_command_message(action)
        return self.send_message(command)


# Global serial communication instance
serial_comm = None


def init_serial_comm(uart_id=0, baudrate=115200, tx_pin=1, rx_pin=3) -> SerialComm:
    """Initialize global serial communication"""
    global serial_comm
    serial_comm = SerialComm(uart_id, baudrate, tx_pin, rx_pin)
    return serial_comm


def get_serial_comm() -> SerialComm:
    """Get the global serial communication instance"""
    return serial_comm


def send_message(message: str) -> bool:
    """Convenience function to send message"""
    if serial_comm:
        return serial_comm.send_message(message)
    return False


def send_command(action: str) -> bool:
    """Convenience function to send command"""
    if serial_comm:
        return serial_comm.send_command(action)
    return False


def check_messages():
    """Convenience function to check for messages"""
    if serial_comm:
        serial_comm.check_for_messages()


def try_reconnect() -> bool:
    """Convenience function to try reconnection"""
    if serial_comm:
        return serial_comm.try_reconnect()
    return False


def is_connected() -> bool:
    """Convenience function to check connection status"""
    if serial_comm:
        return serial_comm.is_connected
    return False
