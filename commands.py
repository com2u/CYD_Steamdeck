"""
Commands module for ESP32-2432S028R (Cheap Yellow Display)
Handles button creation, command structure, and button event handling
"""
from button import ButtonManager, ButtonColors

class CommandHandler:
    """Handles all command-related functionality and button management"""
    
    def __init__(self, display_manager, audio_manager=None):
        self.display_manager = display_manager
        self.audio_manager = audio_manager
        self.button_manager = ButtonManager()
        self.buttons = []
        
    def create_button_interface(self):
        """Create the main button interface"""
        width, height = self.display_manager.get_dimensions()
        
        # Create buttons
        button_texts = ["Init", "Setup", "Test", "Calibrate", "Exit"]
        self.buttons = self.button_manager.create_full_width_buttons(
            width, height, button_texts,
            text_color=ButtonColors.BUTTON_TEXT,
            bg_color=ButtonColors.BUTTON_BG,
            border_color=ButtonColors.BUTTON_BORDER
        )
        
        # Set button callbacks
        self.button_manager.get_button_by_text("Init").set_callback(self.on_init_button)
        self.button_manager.get_button_by_text("Setup").set_callback(self.on_setup_button)
        self.button_manager.get_button_by_text("Test").set_callback(self.on_test_button)
        self.button_manager.get_button_by_text("Calibrate").set_callback(self.on_calibrate_button)
        self.button_manager.get_button_by_text("Exit").set_callback(self.on_exit_button)
        
        return self.buttons
    
    def draw_interface(self):
        """Draw the button interface on the display"""
        if self.display_manager.display:
            self.display_manager.clear_screen()
            self.button_manager.draw_all(self.display_manager.display)
    
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
        """Handle Init button click"""
        print("Init button callback triggered!")
        print("Init button clicked - Initializing system...")
        self.execute_init_command()
    
    def on_setup_button(self, button):
        """Handle Setup button click"""
        print("Setup button clicked - Opening setup menu...")
        self.execute_setup_command()
    
    def on_test_button(self, button):
        """Handle Test button click"""
        print("Test button clicked - Running tests...")
        self.execute_test_command()
    
    def on_calibrate_button(self, button):
        """Handle Calibrate button click"""
        print("Calibrate button clicked - Starting calibration...")
        self.execute_calibrate_command()
    
    def on_exit_button(self, button):
        """Handle Exit button click"""
        print("Exit button clicked - Exiting application...")
        self.execute_exit_command()
    
    # Command execution functions
    def execute_init_command(self):
        """Execute initialization command"""
        print("=== INIT COMMAND ===")
        print("Initializing system components...")
        # Add your initialization logic here
        print("System initialized successfully!")
    
    def execute_setup_command(self):
        """Execute setup command"""
        print("=== SETUP COMMAND ===")
        print("Opening setup configuration...")
        # Add your setup logic here
        print("Setup configuration opened!")
    
    def execute_test_command(self):
        """Execute test command"""
        print("=== TEST COMMAND ===")
        print("Running system tests...")
        # Test display
        if self.display_manager:
            self.display_manager.test_display()
        print("System tests completed!")
    
    def execute_calibrate_command(self):
        """Execute calibration command"""
        print("=== CALIBRATE COMMAND ===")
        print("Starting touch calibration...")
        # Add your calibration logic here
        print("Calibration completed!")
    
    def execute_exit_command(self):
        """Execute exit command"""
        print("=== EXIT COMMAND ===")
        print("Shutting down application...")
        # Add cleanup logic here
        if self.display_manager:
            self.display_manager.set_backlight(False)
        print("Application shutdown complete!")
    
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
