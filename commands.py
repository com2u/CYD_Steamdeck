"""
Commands module for ESP32-2432S028R (Cheap Yellow Display)
Handles button creation, command structure, and button event handling
Enhanced with PC communication and system data display
"""
from button import ButtonManager, ButtonColors
from serial_comm import SerialComm, SystemDataManager
from ili9341 import color565

class CommandHandler:
    """Handles all command-related functionality and button management"""
    
    def __init__(self, display_manager, audio_manager=None):
        self.display_manager = display_manager
        self.audio_manager = audio_manager
        self.button_manager = ButtonManager()
        self.buttons = []
        
        # PC Communication
        self.serial_comm = SerialComm()
        self.system_data = SystemDataManager()
        
        # Display layout
        self.button_width = 120  # Buttons take left half
        self.info_width = 120    # System info takes right half
        self.info_x_offset = 120 # Start info display at x=120
        
    def create_button_interface(self):
        """Create the main button interface with split layout"""
        width, height = self.display_manager.get_dimensions()
        
        # Create buttons for left half only
        button_texts = ["Init", "Test", "Exit"]
        self.buttons = self.button_manager.create_custom_buttons(
            self.button_width, height, button_texts,
            text_color=ButtonColors.BUTTON_TEXT,
            bg_color=ButtonColors.BUTTON_BG,
            border_color=ButtonColors.BUTTON_BORDER
        )
        
        # Set button callbacks
        self.button_manager.get_button_by_text("Init").set_callback(self.on_init_button)
        self.button_manager.get_button_by_text("Test").set_callback(self.on_test_button)
        self.button_manager.get_button_by_text("Exit").set_callback(self.on_exit_button)
        
        return self.buttons
    
    def draw_interface(self):
        """Draw the button interface and system info on the display"""
        if self.display_manager.display:
            self.display_manager.clear_screen()
            self.button_manager.draw_all(self.display_manager.display)
            self.draw_system_info()
    
    def handle_touch_down(self, x, y):
        """Handle touch down event"""
        pressed_button = self.button_manager.handle_touch_down(x, y)
        if pressed_button:
            self.draw_interface()
        return pressed_button
    
    def handle_touch_up(self, x, y):
        """Handle touch up event"""
        clicked_button = self.button_manager.handle_touch_up(x, y)
        if clicked_button:
            # Then play the audio to avoid interference
            if self.audio_manager:
                print(f"Playing click sound for button: {clicked_button.text}")
                self.audio_manager.play_button_click_tone()
            # First redraw the interface
            self.draw_interface()
        return clicked_button
    
    def handle_touch_move(self, x, y):
        """Handle touch move event"""
        self.button_manager.handle_touch_move(x, y)
        self.draw_interface()
    
    # Button callback functions
    def on_init_button(self, button):
        """Handle Init button click - Send command to PC"""
        print("Init button clicked - Sending command to PC...")
        self.serial_comm.send_command("init")
    
    def on_test_button(self, button):
        """Handle Test button click - Send command to PC"""
        print("Test button clicked - Sending command to PC...")
        self.serial_comm.send_command("test")
    
    def on_exit_button(self, button):
        """Handle Exit button click - Send command to PC"""
        print("Exit button clicked - Sending command to PC...")
        self.serial_comm.send_command("exit")
    
    # Communication and display functions
    def update_system_data(self):
        """Update system data from PC"""
        data = self.serial_comm.read_system_data()
        if data:
            self.system_data.update_data(data)
            return True
        return False
    
    def send_heartbeat(self):
        """Send heartbeat to PC"""
        return self.serial_comm.send_heartbeat()
    
    def is_pc_connected(self):
        """Check if PC is connected"""
        return self.serial_comm.is_connected()
    
    def draw_system_info(self):
        """Draw system information on the right side of display"""
        if not self.display_manager.display:
            return
            
        display = self.display_manager.display
        x_start = self.info_x_offset
        y_pos = 10
        line_height = 25
        
        # Colors
        text_color = color565(255, 255, 255)  # White
        label_color = color565(200, 200, 200)  # Light gray
        value_color = color565(0, 255, 0)     # Green
        
        # Connection status
        conn_status = "CONN" if self.is_pc_connected() else "DISC"
        conn_color = color565(0, 255, 0) if self.is_pc_connected() else color565(255, 0, 0)
        display.draw_text8x8(x_start, y_pos, conn_status, conn_color)
        y_pos += line_height
        
        # Date and Time
        date, time = self.system_data.get_datetime_info()
        display.draw_text8x8(x_start, y_pos, date[:10], text_color)
        y_pos += 15
        display.draw_text8x8(x_start, y_pos, time[:8], text_color)
        y_pos += line_height
        
        # CPU Usage
        cpu = self.system_data.get_cpu_percentage()
        cpu_text = f"CPU:{cpu:4.1f}%"
        display.draw_text8x8(x_start, y_pos, cpu_text, value_color)
        y_pos += line_height
        
        # RAM Usage
        ram_used, ram_total = self.system_data.get_ram_info()
        ram_pct = self.system_data.get_ram_percentage()
        ram_text = f"RAM:{ram_pct:4.1f}%"
        display.draw_text8x8(x_start, y_pos, ram_text, value_color)
        y_pos += 15
        ram_detail = f"{ram_used:.1f}/{ram_total:.1f}GB"
        display.draw_text8x8(x_start, y_pos, ram_detail[:12], text_color)
        y_pos += line_height
        
        # Network
        net_sent, net_recv = self.system_data.get_network_info()
        net_sent_text = f"TX:{self.system_data.format_bytes(net_sent)[:8]}"
        net_recv_text = f"RX:{self.system_data.format_bytes(net_recv)[:8]}"
        display.draw_text8x8(x_start, y_pos, net_sent_text, value_color)
        y_pos += 15
        display.draw_text8x8(x_start, y_pos, net_recv_text, value_color)
    
    def get_button_manager(self):
        """Get the button manager instance"""
        return self.button_manager
    
    def clear_all_buttons(self):
        """Clear all button pressed states"""
        self.button_manager.clear_all_pressed()


class MenuSystem:
    """Advanced menu system for more complex interfaces"""
    
    def __init__(self, display_manager):
        self.display_manager = display_manager
        self.current_menu = "main"
        self.menu_stack = []
        self.menus = {}
        self.setup_menus()
    
    def setup_menus(self):
        """Setup different menu configurations"""
        # Main menu
        self.menus["main"] = {
            "title": "Main Menu",
            "buttons": ["Init", "Setup", "Test", "Calibrate", "Exit"],
            "callbacks": [
                self.goto_init_menu,
                self.goto_setup_menu,
                self.goto_test_menu,
                self.goto_calibrate_menu,
                self.exit_application
            ]
        }
        
        # Setup submenu
        self.menus["setup"] = {
            "title": "Setup Menu",
            "buttons": ["WiFi", "Display", "Touch", "System", "Back"],
            "callbacks": [
                self.setup_wifi,
                self.setup_display,
                self.setup_touch,
                self.setup_system,
                self.go_back
            ]
        }
        
        # Test submenu
        self.menus["test"] = {
            "title": "Test Menu",
            "buttons": ["Display", "Touch", "WiFi", "All", "Back"],
            "callbacks": [
                self.test_display,
                self.test_touch,
                self.test_wifi,
                self.test_all,
                self.go_back
            ]
        }
    
    def goto_init_menu(self, button):
        """Go to init menu"""
        print("Initializing system...")
    
    def goto_setup_menu(self, button):
        """Go to setup menu"""
        self.push_menu("setup")
    
    def goto_test_menu(self, button):
        """Go to test menu"""
        self.push_menu("test")
    
    def goto_calibrate_menu(self, button):
        """Go to calibrate menu"""
        print("Starting calibration...")
    
    def exit_application(self, button):
        """Exit the application"""
        print("Exiting application...")
    
    def setup_wifi(self, button):
        """Setup WiFi"""
        print("WiFi setup...")
    
    def setup_display(self, button):
        """Setup display"""
        print("Display setup...")
    
    def setup_touch(self, button):
        """Setup touch"""
        print("Touch setup...")
    
    def setup_system(self, button):
        """Setup system"""
        print("System setup...")
    
    def test_display(self, button):
        """Test display"""
        if self.display_manager:
            self.display_manager.test_display()
    
    def test_touch(self, button):
        """Test touch"""
        print("Touch test...")
    
    def test_wifi(self, button):
        """Test WiFi"""
        print("WiFi test...")
    
    def test_all(self, button):
        """Test all systems"""
        print("Running all tests...")
    
    def go_back(self, button):
        """Go back to previous menu"""
        self.pop_menu()
    
    def push_menu(self, menu_name):
        """Push current menu to stack and switch to new menu"""
        self.menu_stack.append(self.current_menu)
        self.current_menu = menu_name
        self.create_current_menu()
    
    def pop_menu(self):
        """Pop menu from stack and return to previous menu"""
        if self.menu_stack:
            self.current_menu = self.menu_stack.pop()
            self.create_current_menu()
    
    def create_current_menu(self):
        """Create and display the current menu"""
        if self.current_menu in self.menus:
            menu_config = self.menus[self.current_menu]
            print(f"Switching to: {menu_config['title']}")
            # Here you would create buttons based on menu_config
            # This is a simplified version - you'd integrate with ButtonManager
