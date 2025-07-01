"""
Button module for ESP32-2432S028R (Cheap Yellow Display)
Handles button creation, rendering, and touch detection
Updated for new ili9341 Display API
"""
from ili9341 import color565

class Button:
    def __init__(self, x, y, width, height, text, text_color=None, bg_color=None, border_color=None, pressed_color=None):
        """
        Initialize a button
        
        Args:
            x, y: Top-left corner position
            width, height: Button dimensions
            text: Button text
            text_color: Text color (default: white)
            bg_color: Background color (default: dark gray)
            border_color: Border color (default: white)
            pressed_color: Color when pressed (default: medium gray)
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        self.text_color = text_color or color565(0, 0, 0)  # Black
        self.bg_color = bg_color or color565(64, 64, 64)  # Dark gray
        self.border_color = border_color or color565(255, 255, 255)  # White
        self.pressed_color = pressed_color or color565(128, 128, 128)  # Medium gray
        self.is_pressed = False
        self.callback = None
        
    def set_callback(self, callback):
        """Set callback function to be called when button is clicked"""
        self.callback = callback
        
    def contains_point(self, x, y):
        """Check if a point is inside the button"""
        return (self.x <= x <= self.x + self.width and 
                self.y <= y <= self.y + self.height)
    
    def draw(self, display):
        """Draw the button on the display using new Display API"""
        # Choose colors based on pressed state
        bg = self.pressed_color if self.is_pressed else self.bg_color
        
        # Draw button background using fill_rectangle
        display.fill_rectangle(self.x, self.y, self.width, self.height, bg)
        
        # Draw border using draw_rectangle
        display.draw_rectangle(self.x, self.y, self.width, self.height, self.border_color)
        
        # Calculate text position (centered) for larger text
        # Use larger character spacing to simulate bigger text
        char_width = 12  # Increased from 8 to make text appear larger
        char_height = 16  # Increased from 8 to make text appear larger
        
        # Calculate text dimensions
        text_width = len(self.text) * char_width
        text_height = char_height
        text_x = self.x + (self.width - text_width) // 2
        text_y = self.y + (self.height - text_height) // 2
        
        # Draw each character individually with larger spacing
        for i, char in enumerate(self.text):
            char_x = text_x + i * char_width
            
            # Draw the character with bold effect (slight offset)
            display.draw_text8x8(char_x, text_y, char, self.text_color, bg)
            display.draw_text8x8(char_x + 1, text_y, char, self.text_color, bg)  # Bold effect
    
    def set_pressed(self, pressed):
        """Set the pressed state of the button"""
        self.is_pressed = pressed
    
    def handle_click(self):
        """Handle button click - call callback if set"""
        if self.callback:
            self.callback(self)
        print(f"Button '{self.text}' clicked!")


class ButtonManager:
    def __init__(self):
        """Initialize button manager"""
        self.buttons = []
        self.pressed_button = None
        
    def add_button(self, button):
        """Add a button to the manager"""
        self.buttons.append(button)
        
    def create_full_width_buttons(self, display_width, display_height, button_texts, 
                                 text_color=None, bg_color=None, border_color=None):
        """
        Create full-width buttons that divide the screen vertically
        
        Args:
            display_width: Width of the display
            display_height: Height of the display
            button_texts: List of button text strings
            text_color: Text color for all buttons
            bg_color: Background color for all buttons
            border_color: Border color for all buttons
        """
        num_buttons = len(button_texts)
        button_height = display_height // num_buttons
        
        for i, text in enumerate(button_texts):
            y = i * button_height
            # Make sure the last button fills any remaining space
            if i == num_buttons - 1:
                height = display_height - y
            else:
                height = button_height
                
            button = Button(0, y, display_width, height, text, 
                          text_color, bg_color, border_color)
            self.add_button(button)
            
        return self.buttons
    
    def create_custom_buttons(self, button_width, display_height, button_texts,
                             text_color=None, bg_color=None, border_color=None):
        """
        Create custom width buttons that divide the screen vertically
        
        Args:
            button_width: Width of the buttons
            display_height: Height of the display
            button_texts: List of button text strings
            text_color: Text color for all buttons
            bg_color: Background color for all buttons
            border_color: Border color for all buttons
        """
        num_buttons = len(button_texts)
        button_height = display_height // num_buttons
        
        for i, text in enumerate(button_texts):
            y = i * button_height
            # Make sure the last button fills any remaining space
            if i == num_buttons - 1:
                height = display_height - y
            else:
                height = button_height
                
            button = Button(0, y, button_width, height, text, 
                          text_color, bg_color, border_color)
            self.add_button(button)
            
        return self.buttons
    
    def draw_all(self, display):
        """Draw all buttons on the display"""
        for button in self.buttons:
            button.draw(display)
    
    def handle_touch_down(self, x, y):
        """Handle touch down event - find and press button"""
        for button in self.buttons:
            if button.contains_point(x, y):
                button.set_pressed(True)
                self.pressed_button = button
                return button
        return None
    
    def handle_touch_up(self, x, y):
        """Handle touch up event - release button and trigger click if still over button"""
        clicked_button = None
        
        if self.pressed_button:
            # Check if touch up is still over the same button
            if self.pressed_button.contains_point(x, y):
                self.pressed_button.handle_click()
                clicked_button = self.pressed_button
            
            # Release the button
            self.pressed_button.set_pressed(False)
            self.pressed_button = None
            
        return clicked_button
    
    def handle_touch_move(self, x, y):
        """Handle touch move event - update button states"""
        if self.pressed_button:
            # Check if still over the pressed button
            if self.pressed_button.contains_point(x, y):
                self.pressed_button.set_pressed(True)
            else:
                self.pressed_button.set_pressed(False)
    
    def get_button_by_text(self, text):
        """Get button by its text"""
        for button in self.buttons:
            if button.text == text:
                return button
        return None
    
    def clear_all_pressed(self):
        """Clear pressed state from all buttons"""
        for button in self.buttons:
            button.set_pressed(False)
        self.pressed_button = None


# Color constants for buttons using color565 function
class ButtonColors:
    # Basic colors
    BLACK = color565(0, 0, 0)
    WHITE = color565(255, 255, 255)
    RED = color565(255, 0, 0)
    GREEN = color565(0, 255, 0)
    BLUE = color565(0, 0, 255)
    YELLOW = color565(255, 255, 0)
    CYAN = color565(0, 255, 255)
    MAGENTA = color565(255, 0, 255)
    
    # Button specific colors
    BUTTON_BG = color565(64, 64, 64)      # Dark gray
    BUTTON_PRESSED = color565(128, 128, 128)  # Medium gray
    BUTTON_BORDER = color565(255, 255, 255)   # White border
    BUTTON_TEXT = color565(0, 0, 0)       # Black text
    
    # Themed button colors
    INIT_COLOR = color565(0, 255, 0)      # Green
    SETUP_COLOR = color565(0, 0, 255)     # Blue
    TEST_COLOR = color565(255, 255, 0)    # Yellow
    CALIBRATE_COLOR = color565(255, 0, 255) # Magenta
    EXIT_COLOR = color565(255, 0, 0)      # Red
