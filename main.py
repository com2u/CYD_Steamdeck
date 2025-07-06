"""
ESP32 CYD Main Application with PC Communication
Displays buttons, system information, and handles PC communication
"""
import time
import gc
import sys
import select
from display import DisplayManager
from button import Button, ButtonManager, ButtonColors
from audio import AudioManager
# Serial communication handled through USB debug channel only
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
        self.last_usb_check = 0  # For non-blocking USB communication
        self.touch_idle_counter = 0  # For touch-priority architecture
        
        # Non-blocking serial communication
        self.serial_buffer = ""  # Buffer for building messages character by character
        self.message_queue = []  # Queue for complete messages ready to process
        
        # Menu system
        self.button_manager = ButtonManager()
        self.current_menu = "main"
        self.menu_stack = []  # For navigation history
        self.show_system_info = False
        
        # Menu definitions
        self.menus = {
            "main": ["Setup", "System", "Control"],
            "setup": ["Calibrate", "WIFI", "EXIT"],
            "system": ["Control", "EXIT"],
            "control": ["Browser", "Terminal", "Shutdown", "EXIT"]
        }
        
    def create_menu_buttons(self):
        """Create buttons for the current menu"""
        self.button_manager.buttons.clear()  # Clear existing buttons
        
        menu_items = self.menus.get(self.current_menu, [])
        
        if self.current_menu == "system" and self.show_system_info:
            # For system menu, use fixed small height for buttons, leave most space for system info
            available_height = 40  # Fixed 40px total for both buttons (20px each)
            self.button_manager.create_full_width_buttons(
                self.width, available_height, menu_items,
                ButtonColors.BUTTON_TEXT, ButtonColors.BUTTON_BG, ButtonColors.BUTTON_BORDER
            )
        else:
            # Use full screen for buttons
            self.button_manager.create_full_width_buttons(
                self.width, self.height, menu_items,
                ButtonColors.BUTTON_TEXT, ButtonColors.BUTTON_BG, ButtonColors.BUTTON_BORDER
            )
        
        # Set button callbacks
        for button in self.button_manager.buttons:
            button.set_callback(self.handle_menu_button_press)
        
        print(f"Created {len(menu_items)} buttons for menu: {self.current_menu}")
    
    def handle_menu_button_press(self, button):
        """Handle menu button press"""
        button_text = button.text
        print(f"Menu button pressed: {button_text}")
        
        # Audio feedback
        self.audio_manager.play_button_click_tone()
        
        # Handle navigation
        if button_text == "EXIT":
            self.navigate_back()
        elif button_text == "Setup":
            self.navigate_to_menu("setup")
        elif button_text == "System":
            self.navigate_to_menu("system")
            self.show_system_info = True
        elif button_text == "Control":
            self.navigate_to_menu("control")
        elif button_text in ["Browser", "Terminal", "Shutdown"]:
            self.execute_pc_command(button_text)
        elif button_text in ["Calibrate", "WIFI"]:
            print(f"{button_text} functionality will be implemented in the future")
        
        # Redraw interface
        self.draw_interface()
    
    def navigate_to_menu(self, menu_name):
        """Navigate to a specific menu"""
        if menu_name in self.menus:
            self.menu_stack.append(self.current_menu)
            self.current_menu = menu_name
            if menu_name != "system":
                self.show_system_info = False
            self.create_menu_buttons()
            print(f"Navigated to menu: {menu_name}")
    
    def navigate_back(self):
        """Navigate back to previous menu"""
        if self.menu_stack:
            self.current_menu = self.menu_stack.pop()
            self.show_system_info = False
            self.create_menu_buttons()
            print(f"Navigated back to menu: {self.current_menu}")
        else:
            print("Already at main menu")
    
    def execute_pc_command(self, command):
        """Execute PC command via USB debug output"""
        command_map = {
            "Browser": "TEST",    # Maps to Chrome
            "Terminal": "INIT",   # Maps to Terminal
            "Shutdown": "EXIT"    # Maps to Shutdown
        }
        
        pc_command = command_map.get(command, command.upper())
        print(f"PC_COMMAND:{pc_command}")
        print(f"Command {command} sent to PC")
        
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
        
        # Serial communication will be handled through USB debug channel
        # No separate UART needed - system data comes through debug output
        self.serial_comm = None
        print("Using USB debug channel for PC communication")
        
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
        
        # Draw menu buttons
        self.button_manager.draw_all(self.display)
        
        # Draw system information if in system menu
        if self.current_menu == "system" and self.show_system_info:
            self.draw_system_info()
    
    def draw_system_info(self):
        """Draw system information received from PC in bottom half of screen"""
        # Start drawing in the bottom half of the screen
        y = self.height // 2 + 10
        line_height = 16
        
        # Connection status
        current_time = time.time()
        data_is_fresh = (self.last_system_update > 0 and 
                        current_time - self.last_system_update < 30.0)
        
        if data_is_fresh:
            status_text = "Status: Connected"
            status_color = 0x07E0  # Green
        else:
            status_text = "Status: No Data"
            status_color = 0xF800  # Red
        
        self.display.draw_text8x8(10, y, status_text, status_color)
        y += line_height
        
        # Date and Time
        self.display.draw_text8x8(10, y, f"Date: {self.system_data['date']}", 0xFFFF)
        y += line_height
        self.display.draw_text8x8(10, y, f"Time: {self.system_data['time']}", 0xFFFF)
        y += line_height
        
        # CPU Usage
        cpu_text = f"CPU: {self.system_data['cpu_percent']:.1f}%"
        self.display.draw_text8x8(10, y, cpu_text, 0xFFE0)  # Yellow
        y += line_height
        
        # RAM Usage
        ram_text = f"RAM: {self.system_data['ram_used_gb']:.1f}/{self.system_data['ram_total_gb']:.1f}GB"
        self.display.draw_text8x8(10, y, ram_text, 0x07FF)  # Cyan
        y += line_height
        
        # Network Usage
        net_text = f"NET: U:{self.system_data['network_sent_mb']:.1f} D:{self.system_data['network_recv_mb']:.1f}MB"
        self.display.draw_text8x8(10, y, net_text, 0xF81F)  # Magenta
    
    
    def check_touch_input(self):
        """Check for touch input and handle menu button presses"""
        touch_detected = False
        if self.display_manager.is_touched():
            touch_detected = True
            x, y = self.display_manager.get_touch_coordinates()
            print(f"Touch detected at: ({x}, {y})")
            
            # Use button manager to handle touch - need both down and up for proper click
            pressed_button = self.button_manager.handle_touch_down(x, y)
            if pressed_button:
                print(f"Button pressed: {pressed_button.text}")
                # Immediately handle touch up for simple click behavior
                clicked_button = self.button_manager.handle_touch_up(x, y)
                if clicked_button:
                    print(f"Button clicked: {clicked_button.text}")
            
            # Reset touch idle counter when touch is detected
            self.touch_idle_counter = 0
        else:
            # Increment touch idle counter when no touch
            self.touch_idle_counter += 1
        
        return touch_detected
    
    def check_usb_input_nonblocking(self):
        """Non-blocking USB input using brace-based JSON message parsing with smart buffer management"""
        try:
            # Check if ANY data is available (no blocking)
            if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
                # Read single character (non-blocking)
                char = sys.stdin.read(1)
                if char:
                    if char == '{':
                        # Improved buffer management - don't lose substantial data
                        if len(self.serial_buffer) > 50:
                            print(f"WARNING: New message started before completion: {self.serial_buffer[:100]}...")
                            # Try to salvage partial message if it looks like valid JSON start
                            if self.serial_buffer.startswith('{"type":'):
                                print("Attempting to salvage partial message")
                                # Queue partial message for debugging
                                self.message_queue.append(f"PARTIAL: {self.serial_buffer}")
                        
                        # Start new message
                        self.serial_buffer = '{'
                        print("JSON_START: New message started")
                        
                    elif char == '}':
                        # End of JSON message - complete it
                        self.serial_buffer += '}'
                        print(f"JSON_END: Message completed ({len(self.serial_buffer)} chars)")
                        
                        # Validate and queue complete JSON message
                        if self.is_valid_json(self.serial_buffer):
                            self.message_queue.append(self.serial_buffer)
                            print(f"QUEUED_MESSAGE: {self.serial_buffer}")
                        else:
                            print(f"INVALID_JSON: {self.serial_buffer}")
                        
                        # Clear buffer for next message
                        self.serial_buffer = ""
                        
                    else:
                        # Add character to current message (only if we have started with '{')
                        if self.serial_buffer.startswith('{'):
                            self.serial_buffer += char
                        # Ignore characters outside of JSON messages
                        
                    # Prevent buffer overflow
                    if len(self.serial_buffer) > 2000:
                        print("Serial buffer overflow, clearing")
                        self.serial_buffer = ""
        except Exception as e:
            # Ignore errors - stdin might not be available in all environments
            pass
    
    def is_valid_json(self, text):
        """Check if text is valid JSON"""
        try:
            from json_protocol import parse_message
            return parse_message(text) is not None
        except:
            return False
    
    def process_message_queue(self):
        """Process all complete messages from queue"""
        ui_needs_update = False
        
        while self.message_queue:
            message = self.message_queue.pop(0)
            print(f"PROCESSING: {message}")
            
            # Check for direct JSON messages first
            if message.startswith('{"type":'):
                try:
                    from json_protocol import parse_message
                    parsed = parse_message(message)
                    if parsed and parsed.get("type") == "system_data":
                        data = extract_system_data(parsed)
                        if data:
                            self.system_data.update(data)
                            self.last_system_update = time.time()
                            ui_needs_update = True
                            print("System data updated from direct JSON")
                            continue
                except Exception as e:
                    print(f"Error parsing direct JSON: {e}")
            
            # Check for prefixed system data messages
            if message.startswith("PC_SYSTEM_DATA:"):
                print(f"Found PC_SYSTEM_DATA message: {message}")
                if self.parse_debug_system_data(message):
                    ui_needs_update = True
            elif message.startswith("ESP32_DATA:"):
                print(f"Found ESP32_DATA message: {message}")
                if self.parse_esp32_data(message):
                    ui_needs_update = True
            else:
                # Handle other messages
                print(f"PC_MESSAGE: {message}")
        
        # Update UI only if we received new system data
        if ui_needs_update and self.current_menu == "system" and self.show_system_info:
            print("UI update triggered by new system data")
            self.draw_interface()
        
        return ui_needs_update
    
    def update_communication(self):
        """Update communication status with non-blocking USB checks"""
        current_time = time.time()
        
        # Non-blocking character reading (very fast)
        self.check_usb_input_nonblocking()
        
        # Process any complete messages in queue
        self.process_message_queue()
        
        # Debug: Log communication status every 30 seconds
        if current_time - self.last_heartbeat > 30:  # Every 30 seconds
            print(f"Communication status: USB_Debug=True, Last_data={current_time - self.last_system_update:.1f}s ago")
            print(f"Buffer: '{self.serial_buffer}', Queue: {len(self.message_queue)} messages")
            self.last_heartbeat = current_time
    
    def run(self):
        """Main application loop"""
        print("ESP32 CYD Application Starting...")
        
        # Initialize hardware
        self.init_hardware()
        
        # Initialize menu system
        self.create_menu_buttons()
        
        # Draw initial interface
        self.draw_interface()
        
        print("Application ready - waiting for input")
        
        # Main loop with touch-priority architecture
        while True:
            try:
                current_time = time.time()
                
                # Priority 1: ALWAYS check touch input first (never blocked)
                touch_detected = self.check_touch_input()
                
                # Priority 2: Only check serial communication when touch is idle
                if not touch_detected and self.touch_idle_counter > 5:  # After 5 loops without touch
                    self.update_communication()
                    self.touch_idle_counter = 0  # Reset counter after checking serial
                
                # UI updates are now handled only when new data arrives in process_message_queue()
                # No periodic UI updates - makes communication more robust
                
                # Reduced delay for faster touch response
                time.sleep(0.01)  # 10ms for fast touch response
                
                # Periodic garbage collection
                if time.ticks_ms() % 10000 < 50:  # Every ~10 seconds
                    gc.collect()
                    
            except KeyboardInterrupt:
                print("Application interrupted")
                break
            except Exception as e:
                print(f"Error in main loop: {e}")
                time.sleep(1)  # Wait before retrying
        
        print("Application stopped")


def main():
    """Main entry point"""
    app = CYDApplication()
    app.run()


if __name__ == "__main__":
    main()
