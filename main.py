"""
ESP32 CYD Main Application with PC Communication
Displays buttons, system information, and handles PC communication
"""
import time
import gc
from display import DisplayManager
from button import Button
from audio import AudioManager
from serial_comm import init_serial_comm, send_command, check_messages, try_reconnect, is_connected
from json_protocol import extract_system_data, extract_ack_info, MessageType


class CYDApplication:
    """Main application class for ESP32 CYD with PC communication"""
    
    def __init__(self):
        # Initialize components
        self.display_manager = DisplayManager()
        self.audio_manager = AudioManager()
        self.serial_comm = None
        
        # Display and dimensions
        self.display = None
        self.width = 320
        self.height = 240
        
        # System data from PC
        self.system_data = {
            "date": "----/--/--",
            "time": "--:--:--",
            "cpu_percent": 0.0,
            "ram_used_gb": 0.0,
            "ram_total_gb": 0.0,
            "network_sent_mb": 0.0,
            "network_recv_mb": 0.0
        }
        
        # Connection status
        self.pc_connected = False
        self.usb_connected = False
        self.last_system_update = 0
        self.last_heartbeat = 0
        
        # UI Layout
        self.setup_ui_layout()
        
    def setup_ui_layout(self):
        """Setup UI layout with smaller buttons and system info area"""
        # Button configuration - smaller to fit all buttons on screen
        self.button_width = 70  # Reduced from 80
        self.button_height = 35
        self.button_spacing = 8  # Reduced from 10
        
        # Calculate button positions (top row) - ensure they fit in 240px width
        button_start_x = (self.width - (3 * self.button_width + 2 * self.button_spacing)) // 2
        button_y = 30
        
        # Create buttons
        self.buttons = [
            Button(button_start_x, button_y, self.button_width, self.button_height, 
                   "Init", 0xFFFF, 0x001F),  # White text, Blue background
            Button(button_start_x + self.button_width + self.button_spacing, button_y, 
                   self.button_width, self.button_height, "Test", 0xFFFF, 0x07E0),  # White text, Green background
            Button(button_start_x + 2 * (self.button_width + self.button_spacing), button_y, 
                   self.button_width, self.button_height, "Exit", 0xFFFF, 0xF800)   # White text, Red background
        ]
        
        # System info area (below buttons)
        self.info_start_y = button_y + self.button_height + 20
        self.info_line_height = 16
        
    def init_hardware(self):
        """Initialize all hardware components"""
        print("Initializing ESP32 CYD hardware...")
        
        # Initialize display
        self.display = self.display_manager.init_display()
        self.width, self.height = self.display_manager.get_dimensions()
        print(f"Display initialized: {self.width}x{self.height}")
        
        # Initialize touch
        self.display_manager.init_touch()
        print("Touch initialized")
        
        # Initialize audio
        self.audio_manager.init_speaker()
        self.audio_manager.play_startup_tone()
        print("Audio initialized")
        
        # Initialize serial communication (use UART 2 to avoid conflict with USB debug)
        self.serial_comm = init_serial_comm(uart_id=2, tx_pin=17, rx_pin=16)
        self.serial_comm.set_message_callback(self.handle_pc_message)
        self.serial_comm.set_connection_callback(self.handle_connection_change)
        
        # Try to connect UART 2
        if self.serial_comm.init_uart():
            print("UART 2 serial communication initialized")
        else:
            print("UART 2 serial communication failed to initialize - will retry")
        
    def handle_pc_message(self, message, is_json):
        """Handle messages received from PC"""
        # Debug: Echo all received messages
        print(f"RECEIVED: {'JSON' if is_json else 'TEXT'}: {message}")
        
        if is_json:
            message_type = message.get("type")
            print(f"JSON Message Type: {message_type}")
            
            if message_type == MessageType.SYSTEM_DATA:
                # Update system data
                data = extract_system_data(message)
                print(f"Extracted system data: {data}")
                if data:
                    self.system_data.update(data)
                    self.last_system_update = time.time()
                    print("System data updated from JSON")
                    
            elif message_type == MessageType.ACK:
                # Handle command acknowledgment
                command, result, details = extract_ack_info(message)
                print(f"Command {command} result: {result}")
                if details:
                    print(f"Details: {details}")
                    
            elif message_type == MessageType.STATUS:
                state = message.get("state")
                print(f"PC Status: {state}")
        else:
            # Non-JSON message (debug output) - check for data messages
            if message.startswith("ESP32_DATA:"):
                print(f"Found ESP32_DATA message: {message}")
                if self.parse_esp32_data(message):
                    return  # Successfully parsed data, don't print as debug
            elif message.startswith("PC_SYSTEM_DATA:"):
                print(f"Found PC_SYSTEM_DATA message: {message}")
                if self.parse_debug_system_data(message):
                    return  # Successfully parsed data, don't print as debug
            print(f"PC: {message}")
    
    def parse_esp32_data(self, debug_message):
        """Parse system data from ESP32_DATA debug output"""
        try:
            if debug_message.startswith("ESP32_DATA:"):
                json_str = debug_message.split("ESP32_DATA:")[1].strip()
                # Try to parse the JSON using the same method as regular messages
                from json_protocol import parse_message
                message = parse_message(json_str)
                
                if message and message.get("type") == MessageType.SYSTEM_DATA:
                    data = extract_system_data(message)
                    if data:
                        self.system_data.update(data)
                        self.last_system_update = time.time()
                        print("System data updated from ESP32_DATA")
                        return True
        except Exception as e:
            print(f"Error parsing ESP32_DATA: {e}")
        return False
    
    def parse_debug_system_data(self, debug_message):
        """Parse system data from debug output"""
        try:
            if debug_message.startswith("PC_SYSTEM_DATA:"):
                json_str = debug_message.split("PC_SYSTEM_DATA:")[1].strip()
                # Try to parse the JSON using the same method as regular messages
                from json_protocol import parse_message
                message = parse_message(json_str)
                
                if message and message.get("type") == MessageType.SYSTEM_DATA:
                    data = extract_system_data(message)
                    if data:
                        self.system_data.update(data)
                        self.last_system_update = time.time()
                        print("System data updated from PC_SYSTEM_DATA")
                        return True
        except Exception as e:
            print(f"Error parsing PC_SYSTEM_DATA: {e}")
        return False
    
    def reset_system_data(self):
        """Reset system data to show no data available"""
        self.system_data = {
            "date": "No Data",
            "time": "No Data",
            "cpu_percent": 0.0,
            "ram_used_gb": 0.0,
            "ram_total_gb": 0.0,
            "network_sent_mb": 0.0,
            "network_recv_mb": 0.0
        }
    
    def handle_connection_change(self, connected):
        """Handle serial connection state changes"""
        self.pc_connected = connected
        if connected:
            print("Connected to PC!")
        else:
            print("Disconnected from PC")
    
    def draw_interface(self):
        """Draw the complete user interface"""
        # Clear display
        self.display_manager.clear_screen()
        
        # Draw title
        self.display.draw_text8x8(10, 5, "ESP32 CYD Control", 0xFFFF)
        
        # Draw connection status based on actual data reception
        current_time = time.time()
        data_is_fresh = (self.last_system_update > 0 and 
                        current_time - self.last_system_update < 30.0)
        
        if data_is_fresh:
            status_text = "OK"
            status_color = 0x07E0  # Green - receiving data
        else:
            status_text = "..."
            status_color = 0xF800  # Red - no data
        
        self.display.draw_text8x8(200, 5, status_text, status_color)
        
        # Draw buttons
        for button in self.buttons:
            button.draw(self.display)
        
        # Draw system information
        self.draw_system_info()
    
    def draw_system_info(self):
        """Draw system information received from PC"""
        y = self.info_start_y
        
        # Date and Time - split into two lines for better readability
        self.display.draw_text8x8(10, y, f"Date: {self.system_data['date']}", 0xFFFF)
        y += self.info_line_height
        self.display.draw_text8x8(10, y, f"Time: {self.system_data['time']}", 0xFFFF)
        y += self.info_line_height
        
        # CPU Usage
        cpu_text = f"CPU: {self.system_data['cpu_percent']:.1f}%"
        self.display.draw_text8x8(10, y, cpu_text, 0xFFE0)  # Yellow
        y += self.info_line_height
        
        # RAM Usage
        ram_text = f"RAM: {self.system_data['ram_used_gb']:.1f}/{self.system_data['ram_total_gb']:.1f} GB"
        self.display.draw_text8x8(10, y, ram_text, 0x07FF)  # Cyan
        y += self.info_line_height
        
        # Network Usage
        net_text = f"NET: U:{self.system_data['network_sent_mb']:.1f} D:{self.system_data['network_recv_mb']:.1f} MB"
        self.display.draw_text8x8(10, y, net_text, 0xF81F)  # Magenta
        
        # Last update time
        if self.last_system_update > 0:
            age = time.time() - self.last_system_update
            if age < 60:
                age_text = f"Updated {age:.0f}s ago"
            else:
                age_text = "Data outdated"
            self.display.draw_text8x8(10, y + self.info_line_height, age_text, 0x8410)  # Gray
    
    def handle_button_press(self, button_index):
        """Handle button press with audio feedback and command execution"""
        button = self.buttons[button_index]
        
        # Visual feedback
        button.set_pressed(True)
        button.draw(self.display)
        
        # Audio feedback
        self.audio_manager.play_button_click_tone()
        
        # Get command
        command_name = button.text
        print(f"Button pressed: {command_name}")
        
        # Send command to PC via both UART and USB debug output
        command_upper = command_name.upper()
        
        # Send via UART (if connected)
        if self.pc_connected:
            if send_command(command_upper):
                print(f"Command {command_name} sent via UART")
            else:
                print(f"Failed to send command via UART")
        
        # Also send via USB debug output for PC Service to parse
        print(f"PC_COMMAND:{command_upper}")
        print(f"Command {command_name} sent to PC")
        
        # Wait a bit then restore button
        time.sleep(0.2)
        button.set_pressed(False)
        button.draw(self.display)
    
    def check_touch_input(self):
        """Check for touch input and handle button presses"""
        if self.display_manager.is_touched():
            x, y = self.display_manager.get_touch_coordinates()
            print(f"Touch detected at: ({x}, {y})")
            
            # Check which button was pressed
            for i, button in enumerate(self.buttons):
                if button.contains_point(x, y):
                    self.handle_button_press(i)
                    break
    
    def update_communication(self):
        """Update serial communication"""
        # Check for incoming messages from UART 2
        check_messages()
        
        # Try to reconnect if not connected
        if not is_connected():
            try_reconnect()
        
        # TEMPORARY: Update with test data to verify display works
        current_time = time.time()
        if current_time - self.last_system_update > 10:  # Every 10 seconds
            self.system_data.update({
                "date": "2025-07-02",
                "time": "17:25:xx",
                "cpu_percent": 15.5,
                "ram_used_gb": 19.0,
                "ram_total_gb": 31.7,
                "network_sent_mb": 73.1,
                "network_recv_mb": 184.3
            })
            self.last_system_update = current_time
            print("TEST: System data updated with test values")
        
        # Send periodic heartbeat
        if current_time - self.last_heartbeat > 30:  # Every 30 seconds
            if self.serial_comm and self.serial_comm.is_connected:
                self.serial_comm.send_heartbeat()
                self.last_heartbeat = current_time
    
    def run(self):
        """Main application loop"""
        print("ESP32 CYD Application Starting...")
        
        # Initialize hardware
        self.init_hardware()
        
        # Draw initial interface
        self.draw_interface()
        
        print("Application ready - waiting for input")
        
        last_ui_update = 0
        
        # Main loop
        while True:
            try:
                current_time = time.time()
                
                # Check touch input
                self.check_touch_input()
                
                # Update communication
                self.update_communication()
                
                # Update UI periodically
                if current_time - last_ui_update > 10.0:  # Every 10 seconds
                    self.draw_interface()
                    last_ui_update = current_time
                
                # Small delay to prevent excessive polling
                time.sleep(0.05)
                
                # Periodic garbage collection
                if time.ticks_ms() % 10000 < 50:  # Every ~10 seconds
                    gc.collect()
                    
            except KeyboardInterrupt:
                print("Application interrupted")
                break
            except Exception as e:
                print(f"Error in main loop: {e}")
                time.sleep(1)  # Wait before retrying
        
        # Cleanup
        if self.serial_comm:
            self.serial_comm.deinit_uart()
        
        print("Application stopped")


def main():
    """Main entry point"""
    app = CYDApplication()
    app.run()


if __name__ == "__main__":
    main()
