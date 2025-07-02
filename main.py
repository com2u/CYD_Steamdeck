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
        self.last_system_update = 0
        self.last_heartbeat = 0
        
        # UI Layout
        self.setup_ui_layout()
        
    def setup_ui_layout(self):
        """Setup UI layout with smaller buttons and system info area"""
        # Button configuration - smaller to make room for system info
        self.button_width = 80
        self.button_height = 35
        self.button_spacing = 10
        
        # Calculate button positions (top row)
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
        
        # Initialize serial communication (use UART 2 to avoid conflict with USB)
        self.serial_comm = init_serial_comm(uart_id=2, tx_pin=17, rx_pin=16)
        self.serial_comm.set_message_callback(self.handle_pc_message)
        self.serial_comm.set_connection_callback(self.handle_connection_change)
        
        # Try to connect
        if self.serial_comm.init_uart():
            print("Serial communication initialized")
        else:
            print("Serial communication failed to initialize - will retry")
        
    def handle_pc_message(self, message, is_json):
        """Handle messages received from PC"""
        if is_json:
            message_type = message.get("type")
            
            if message_type == MessageType.SYSTEM_DATA:
                # Update system data
                data = extract_system_data(message)
                if data:
                    self.system_data.update(data)
                    self.last_system_update = time.time()
                    print("System data updated")
                    
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
            # Non-JSON message (debug output)
            print(f"PC: {message}")
    
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
        self.display.text("ESP32 CYD Control", 10, 5, 0xFFFF)
        
        # Draw connection status
        status_text = "PC: Connected" if self.pc_connected else "PC: Disconnected"
        status_color = 0x07E0 if self.pc_connected else 0xF800  # Green if connected, Red if not
        self.display.text(status_text, 200, 5, status_color)
        
        # Draw buttons
        for button in self.buttons:
            button.draw(self.display)
        
        # Draw system information
        self.draw_system_info()
    
    def draw_system_info(self):
        """Draw system information received from PC"""
        y = self.info_start_y
        
        # Date and Time
        date_time = f"{self.system_data['date']} {self.system_data['time']}"
        self.display.text(f"Date/Time: {date_time}", 10, y, 0xFFFF)
        y += self.info_line_height
        
        # CPU Usage
        cpu_text = f"CPU: {self.system_data['cpu_percent']:.1f}%"
        self.display.text(cpu_text, 10, y, 0xFFE0)  # Yellow
        y += self.info_line_height
        
        # RAM Usage
        ram_text = f"RAM: {self.system_data['ram_used_gb']:.1f}/{self.system_data['ram_total_gb']:.1f} GB"
        self.display.text(ram_text, 10, y, 0x07FF)  # Cyan
        y += self.info_line_height
        
        # Network Usage
        net_text = f"NET: U:{self.system_data['network_sent_mb']:.1f} D:{self.system_data['network_recv_mb']:.1f} MB"
        self.display.text(net_text, 10, y, 0xF81F)  # Magenta
        
        # Last update time
        if self.last_system_update > 0:
            age = time.time() - self.last_system_update
            if age < 60:
                age_text = f"Updated {age:.0f}s ago"
            else:
                age_text = "Data outdated"
            self.display.text(age_text, 10, y + self.info_line_height, 0x8410)  # Gray
    
    def handle_button_press(self, button_index):
        """Handle button press with audio feedback and command execution"""
        button = self.buttons[button_index]
        
        # Visual feedback
        button.set_pressed(True)
        button.draw(self.display)
        
        # Audio feedback
        self.audio_manager.play_beep()
        
        # Get command
        command_name = button.text
        print(f"Button pressed: {command_name}")
        
        # Send command to PC
        if self.pc_connected:
            if send_command(command_name.upper()):
                print(f"Command {command_name} sent to PC")
            else:
                print(f"Failed to send command {command_name}")
        else:
            print("Cannot send command - PC not connected")
        
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
        # Check for incoming messages
        check_messages()
        
        # Try to reconnect if not connected
        if not is_connected():
            try_reconnect()
        
        # Send periodic heartbeat
        current_time = time.time()
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
                if current_time - last_ui_update > 5.0:  # Every 5 seconds
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
