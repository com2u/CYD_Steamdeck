"""
Serial Communication module for ESP32-2432S028R (Cheap Yellow Display)
Handles bidirectional communication with PC service via USB serial
"""
import json
import time
from machine import UART, Pin

class SerialComm:
    """Handles serial communication with PC"""
    
    def __init__(self, uart_id=0, baudrate=115200, tx_pin=1, rx_pin=3):
        """
        Initialize serial communication
        
        Args:
            uart_id: UART interface ID (0 for USB serial)
            baudrate: Communication speed
            tx_pin: TX pin (default 1 for USB)
            rx_pin: RX pin (default 3 for USB)
        """
        self.uart = UART(uart_id, baudrate=baudrate, tx=Pin(tx_pin), rx=Pin(rx_pin))
        self.uart.init(baudrate=baudrate, bits=8, parity=None, stop=1)
        self.connected = False
        self.last_heartbeat = 0
        self.heartbeat_interval = 5000  # 5 seconds
        
    def send_command(self, action):
        """
        Send command to PC
        
        Args:
            action: Command action string (e.g., "init", "test", "exit")
        """
        try:
            message = {
                "type": "command",
                "action": action,
                "timestamp": time.ticks_ms()
            }
            
            json_str = json.dumps(message) + "\n"
            self.uart.write(json_str.encode('utf-8'))
            print(f"Sent command: {action}")
            return True
            
        except Exception as e:
            print(f"Error sending command: {e}")
            return False
    
    def send_heartbeat(self):
        """Send heartbeat to maintain connection"""
        current_time = time.ticks_ms()
        if time.ticks_diff(current_time, self.last_heartbeat) > self.heartbeat_interval:
            try:
                message = {
                    "type": "heartbeat",
                    "timestamp": current_time
                }
                json_str = json.dumps(message) + "\n"
                self.uart.write(json_str.encode('utf-8'))
                self.last_heartbeat = current_time
                return True
            except Exception as e:
                print(f"Error sending heartbeat: {e}")
                return False
        return True
    
    def read_system_data(self):
        """
        Read system data from PC
        
        Returns:
            dict: System data or None if no data available
        """
        try:
            if self.uart.any():
                # Read available data
                data = self.uart.read()
                if data:
                    # Convert bytes to string
                    data_str = data.decode('utf-8').strip()
                    
                    # Handle multiple messages (split by newlines)
                    lines = data_str.split('\n')
                    
                    for line in lines:
                        if line.strip():
                            try:
                                message = json.loads(line.strip())
                                if message.get("type") == "system_data":
                                    self.connected = True
                                    return message
                                elif message.get("type") == "heartbeat_ack":
                                    self.connected = True
                            except json.JSONDecodeError:
                                print(f"Invalid JSON received: {line}")
                                continue
                                
        except Exception as e:
            print(f"Error reading system data: {e}")
            self.connected = False
            
        return None
    
    def is_connected(self):
        """Check if connected to PC service"""
        return self.connected
    
    def set_connected(self, status):
        """Set connection status"""
        self.connected = status
    
    def flush_input(self):
        """Flush input buffer"""
        try:
            while self.uart.any():
                self.uart.read()
        except Exception as e:
            print(f"Error flushing input: {e}")


class SystemDataManager:
    """Manages system data received from PC"""
    
    def __init__(self):
        self.cpu_usage = 0.0
        self.ram_used = 0.0
        self.ram_total = 0.0
        self.net_sent = 0
        self.net_recv = 0
        self.date = "----/--/--"
        self.time = "--:--:--"
        self.last_update = 0
        self.data_timeout = 10000  # 10 seconds
        
    def update_data(self, system_data):
        """
        Update system data from received message
        
        Args:
            system_data: Dictionary containing system information
        """
        try:
            self.cpu_usage = system_data.get("cpu", 0.0)
            self.ram_used = system_data.get("ram_used", 0.0)
            self.ram_total = system_data.get("ram_total", 0.0)
            self.net_sent = system_data.get("net_sent", 0)
            self.net_recv = system_data.get("net_recv", 0)
            self.date = system_data.get("date", "----/--/--")
            self.time = system_data.get("time", "--:--:--")
            self.last_update = time.ticks_ms()
            
            print(f"System data updated - CPU: {self.cpu_usage}%, RAM: {self.ram_used}/{self.ram_total}GB")
            
        except Exception as e:
            print(f"Error updating system data: {e}")
    
    def is_data_fresh(self):
        """Check if system data is recent"""
        current_time = time.ticks_ms()
        return time.ticks_diff(current_time, self.last_update) < self.data_timeout
    
    def get_cpu_percentage(self):
        """Get CPU usage as percentage"""
        return self.cpu_usage if self.is_data_fresh() else 0.0
    
    def get_ram_info(self):
        """Get RAM usage information"""
        if self.is_data_fresh():
            return self.ram_used, self.ram_total
        return 0.0, 0.0
    
    def get_ram_percentage(self):
        """Get RAM usage as percentage"""
        if self.is_data_fresh() and self.ram_total > 0:
            return (self.ram_used / self.ram_total) * 100
        return 0.0
    
    def get_network_info(self):
        """Get network transfer information"""
        if self.is_data_fresh():
            return self.net_sent, self.net_recv
        return 0, 0
    
    def get_datetime_info(self):
        """Get date and time information"""
        if self.is_data_fresh():
            return self.date, self.time
        return "----/--/--", "--:--:--"
    
    def format_bytes(self, bytes_value):
        """Format bytes to human readable format"""
        if bytes_value < 1024:
            return f"{bytes_value}B"
        elif bytes_value < 1024 * 1024:
            return f"{bytes_value/1024:.1f}KB"
        elif bytes_value < 1024 * 1024 * 1024:
            return f"{bytes_value/(1024*1024):.1f}MB"
        else:
            return f"{bytes_value/(1024*1024*1024):.1f}GB"
