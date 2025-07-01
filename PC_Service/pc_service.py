"""
PC Service for ESP32-2432S028R Communication
Handles bidirectional communication with ESP32 display via USB serial
Executes commands and sends system monitoring data
"""
import serial
import json
import time
import threading
import psutil
import subprocess
import sys
from datetime import datetime
import os

class PCService:
    """Main PC service for ESP32 communication"""
    
    def __init__(self, port='COM3', baudrate=115200):
        """
        Initialize PC service
        
        Args:
            port: Serial port (e.g., 'COM3' on Windows, '/dev/ttyUSB0' on Linux)
            baudrate: Communication speed
        """
        self.port = port
        self.baudrate = baudrate
        self.serial_conn = None
        self.running = False
        self.system_monitor = SystemMonitor()
        self.command_executor = CommandExecutor()
        
        # Threading
        self.read_thread = None
        self.write_thread = None
        
        # Connection status
        self.connected = False
        self.last_heartbeat = 0
        
    def connect(self):
        """Connect to ESP32 via serial"""
        try:
            self.serial_conn = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=1,
                write_timeout=1
            )
            
            # Wait for connection to stabilize
            time.sleep(2)
            
            # Flush any existing data
            self.serial_conn.flushInput()
            self.serial_conn.flushOutput()
            
            self.connected = True
            print(f"Connected to ESP32 on {self.port}")
            return True
            
        except serial.SerialException as e:
            print(f"Failed to connect to {self.port}: {e}")
            return False
        except Exception as e:
            print(f"Unexpected error connecting: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from ESP32"""
        self.running = False
        self.connected = False
        
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.close()
            print("Disconnected from ESP32")
    
    def start_service(self):
        """Start the PC service"""
        if not self.connect():
            return False
        
        self.running = True
        
        # Start communication threads
        self.read_thread = threading.Thread(target=self._read_loop, daemon=True)
        self.write_thread = threading.Thread(target=self._write_loop, daemon=True)
        
        self.read_thread.start()
        self.write_thread.start()
        
        print("PC Service started successfully")
        print("Listening for ESP32 commands...")
        print("Press Ctrl+C to stop")
        
        try:
            # Keep main thread alive
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nShutting down PC Service...")
            self.stop_service()
        
        return True
    
    def stop_service(self):
        """Stop the PC service"""
        self.running = False
        self.disconnect()
        
        # Wait for threads to finish
        if self.read_thread and self.read_thread.is_alive():
            self.read_thread.join(timeout=2)
        if self.write_thread and self.write_thread.is_alive():
            self.write_thread.join(timeout=2)
        
        print("PC Service stopped")
    
    def _read_loop(self):
        """Read messages from ESP32"""
        while self.running and self.connected:
            try:
                if self.serial_conn and self.serial_conn.in_waiting > 0:
                    # Read line from serial
                    line = self.serial_conn.readline().decode('utf-8').strip()
                    
                    if line:
                        try:
                            message = json.loads(line)
                            self._handle_message(message)
                        except json.JSONDecodeError:
                            print(f"Invalid JSON received: {line}")
                
                time.sleep(0.1)  # Small delay to prevent busy waiting
                
            except serial.SerialException as e:
                print(f"Serial read error: {e}")
                self.connected = False
                break
            except Exception as e:
                print(f"Unexpected read error: {e}")
                time.sleep(1)
    
    def _write_loop(self):
        """Send system data to ESP32"""
        while self.running and self.connected:
            try:
                # Get current system data
                system_data = self.system_monitor.get_system_data()
                
                # Create message
                message = {
                    "type": "system_data",
                    **system_data
                }
                
                # Send to ESP32
                self._send_message(message)
                
                # Wait before next update
                time.sleep(1)  # Send data every second
                
            except Exception as e:
                print(f"Write loop error: {e}")
                time.sleep(1)
    
    def _handle_message(self, message):
        """Handle incoming message from ESP32"""
        msg_type = message.get("type")
        
        if msg_type == "command":
            action = message.get("action")
            print(f"Received command: {action}")
            
            # Execute command
            success = self.command_executor.execute_command(action)
            
            if success:
                print(f"Command '{action}' executed successfully")
            else:
                print(f"Command '{action}' failed")
                
        elif msg_type == "heartbeat":
            # Respond to heartbeat
            response = {
                "type": "heartbeat_ack",
                "timestamp": int(time.time() * 1000)
            }
            self._send_message(response)
            self.last_heartbeat = time.time()
            
        else:
            print(f"Unknown message type: {msg_type}")
    
    def _send_message(self, message):
        """Send message to ESP32"""
        try:
            if self.serial_conn and self.serial_conn.is_open:
                json_str = json.dumps(message) + "\n"
                self.serial_conn.write(json_str.encode('utf-8'))
                return True
        except Exception as e:
            print(f"Error sending message: {e}")
            return False


class SystemMonitor:
    """Monitors system resources"""
    
    def __init__(self):
        self.net_io_start = psutil.net_io_counters()
        self.last_net_check = time.time()
        
    def get_system_data(self):
        """Get current system data"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=None)
            
            # Memory usage
            memory = psutil.virtual_memory()
            ram_used_gb = memory.used / (1024**3)
            ram_total_gb = memory.total / (1024**3)
            
            # Network I/O
            current_net = psutil.net_io_counters()
            current_time = time.time()
            
            # Calculate network rates (bytes per second)
            time_diff = current_time - self.last_net_check
            if time_diff > 0:
                net_sent_rate = (current_net.bytes_sent - self.net_io_start.bytes_sent) / time_diff
                net_recv_rate = (current_net.bytes_recv - self.net_io_start.bytes_recv) / time_diff
            else:
                net_sent_rate = 0
                net_recv_rate = 0
            
            # Update for next calculation
            self.net_io_start = current_net
            self.last_net_check = current_time
            
            # Date and time
            now = datetime.now()
            date_str = now.strftime("%Y-%m-%d")
            time_str = now.strftime("%H:%M:%S")
            
            return {
                "cpu": round(cpu_percent, 1),
                "ram_used": round(ram_used_gb, 1),
                "ram_total": round(ram_total_gb, 1),
                "net_sent": int(net_sent_rate),
                "net_recv": int(net_recv_rate),
                "date": date_str,
                "time": time_str
            }
            
        except Exception as e:
            print(f"Error getting system data: {e}")
            return {
                "cpu": 0.0,
                "ram_used": 0.0,
                "ram_total": 0.0,
                "net_sent": 0,
                "net_recv": 0,
                "date": "----/--/--",
                "time": "--:--:--"
            }


class CommandExecutor:
    """Executes commands received from ESP32"""
    
    def execute_command(self, action):
        """
        Execute command based on action
        
        Args:
            action: Command action string
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if action == "init":
                return self._start_terminal()
            elif action == "test":
                return self._start_chrome()
            elif action == "exit":
                return self._shutdown_system()
            else:
                print(f"Unknown command: {action}")
                return False
                
        except Exception as e:
            print(f"Error executing command '{action}': {e}")
            return False
    
    def _start_terminal(self):
        """Start Windows Terminal"""
        try:
            # Try Windows Terminal first, fallback to cmd
            try:
                subprocess.Popen(['wt'], shell=True)
                print("Started Windows Terminal")
            except FileNotFoundError:
                subprocess.Popen(['cmd'], shell=True)
                print("Started Command Prompt")
            return True
        except Exception as e:
            print(f"Failed to start terminal: {e}")
            return False
    
    def _start_chrome(self):
        """Start Chrome browser"""
        try:
            # Common Chrome paths on Windows
            chrome_paths = [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                r"C:\Users\{}\AppData\Local\Google\Chrome\Application\chrome.exe".format(os.getenv('USERNAME'))
            ]
            
            for path in chrome_paths:
                if os.path.exists(path):
                    subprocess.Popen([path])
                    print("Started Chrome browser")
                    return True
            
            # Fallback: try to start via shell
            subprocess.Popen(['start', 'chrome'], shell=True)
            print("Started Chrome browser (via shell)")
            return True
            
        except Exception as e:
            print(f"Failed to start Chrome: {e}")
            return False
    
    def _shutdown_system(self):
        """Shutdown the system (with confirmation)"""
        try:
            print("SHUTDOWN COMMAND RECEIVED!")
            print("System will shutdown in 60 seconds...")
            print("Run 'shutdown /a' to cancel")
            
            # Schedule shutdown in 60 seconds with message
            subprocess.Popen([
                'shutdown', '/s', '/t', '60', 
                '/c', 'Shutdown initiated by ESP32 display. Run "shutdown /a" to cancel.'
            ])
            return True
            
        except Exception as e:
            print(f"Failed to shutdown system: {e}")
            return False


def find_esp32_port():
    """Try to automatically find ESP32 serial port"""
    import serial.tools.list_ports
    
    ports = serial.tools.list_ports.comports()
    
    for port in ports:
        # Look for common ESP32 identifiers
        if any(keyword in port.description.lower() for keyword in ['esp32', 'cp210', 'ch340', 'usb serial']):
            print(f"Found potential ESP32 port: {port.device} - {port.description}")
            return port.device
    
    # If no ESP32 found, list all available ports
    print("Available serial ports:")
    for port in ports:
        print(f"  {port.device} - {port.description}")
    
    return None


def main():
    """Main function"""
    print("=== ESP32 PC Service ===")
    print("Starting PC service for ESP32 communication...")
    
    # Try to find ESP32 port automatically
    port = find_esp32_port()
    
    if not port:
        # Ask user for port if not found automatically
        port = input("Enter serial port (e.g., COM3): ").strip()
        if not port:
            print("No port specified. Exiting.")
            return
    
    # Create and start service
    service = PCService(port=port)
    
    try:
        service.start_service()
    except Exception as e:
        print(f"Service error: {e}")
    finally:
        service.stop_service()


if __name__ == "__main__":
    main()
