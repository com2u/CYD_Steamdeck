"""
Display module for ESP32-2432S028R (Cheap Yellow Display)
Handles display initialization, colors, pin setup, and touch functionality
"""
import time
from machine import Pin, SPI
from ili9341 import Display, color565

# Display pins for ESP32-2432S028R (Cheap Yellow Display)
TFT_CLK_PIN = 14
TFT_MOSI_PIN = 13
TFT_MISO_PIN = 12
TFT_CS_PIN = 15
TFT_DC_PIN = 2
TFT_RST_PIN = 4
TFT_BL_PIN = 21  # Backlight control

# Touch pins
TOUCH_CLK_PIN = 25
TOUCH_MOSI_PIN = 32
TOUCH_MISO_PIN = 39
TOUCH_CS_PIN = 33
TOUCH_IRQ_PIN = 36

# XPT2046 commands
_GET_X = const(0xD0)
_GET_Y = const(0x90)
_GET_Z1 = const(0xB0)
_GET_Z2 = const(0xC0)

# Display dimensions
WIDTH = 240
HEIGHT = 320

# Colors using color565 function
BLACK = color565(0, 0, 0)
WHITE = color565(255, 255, 255)
BLUE = color565(0, 0, 255)
RED = color565(255, 0, 0)
GREEN = color565(0, 255, 0)
YELLOW = color565(255, 255, 0)
CYAN = color565(0, 255, 255)
MAGENTA = color565(255, 0, 255)

class DisplayManager:
    """Manages display and touch functionality"""
    
    def __init__(self):
        self.display = None
        self.spi_touch = None
        self.touch_cs = None
        self.backlight = None
        
    def init_display(self):
        """Initialize the display with the new Display class"""
        # Configure SPI for display
        spi_tft = SPI(1, baudrate=40000000, sck=Pin(TFT_CLK_PIN), mosi=Pin(TFT_MOSI_PIN))
        
        # Configure display pins
        display_cs = Pin(TFT_CS_PIN, Pin.OUT)
        display_dc = Pin(TFT_DC_PIN, Pin.OUT)
        display_rst = Pin(TFT_RST_PIN, Pin.OUT)
        
        # Initialize backlight
        self.backlight = Pin(TFT_BL_PIN, Pin.OUT)
        self.backlight.value(1)  # Turn on backlight
        
        # Initialize display with new Display class
        # rotation=90 for landscape mode (equivalent to old rotation=1)
        self.display = Display(
            spi=spi_tft,
            cs=display_cs,
            dc=display_dc,
            rst=display_rst,
            width=WIDTH,
            height=HEIGHT,
            rotation=90  # 90 degrees for landscape orientation
        )
        
        return self.display

    def init_touch(self):
        """Initialize the touch controller"""
        # Configure SPI for touch
        self.spi_touch = SPI(2, baudrate=2000000, sck=Pin(TOUCH_CLK_PIN), 
                           mosi=Pin(TOUCH_MOSI_PIN), miso=Pin(TOUCH_MISO_PIN))
        
        # Configure touch CS pin
        self.touch_cs = Pin(TOUCH_CS_PIN, Pin.OUT)
        self.touch_cs.value(1)  # CS high when not in use
        
        return self.spi_touch, self.touch_cs

    def read_touch(self, command):
        """Read raw touch data"""
        self.touch_cs.value(0)
        self.spi_touch.write(bytearray([command]))
        result = self.spi_touch.read(2)
        self.touch_cs.value(1)
        
        if len(result) == 2:
            return (result[0] << 8 | result[1]) >> 3
        return 0

    def is_touched(self, threshold=1000):
        """Check if the screen is being touched"""
        z1 = self.read_touch(_GET_Z1)
        z2 = self.read_touch(_GET_Z2)
        
        if z2 == 0:
            return False
            
        z = z1 + 4095 - z2
        return z > threshold

    def get_touch_coordinates(self):
        """Get touch coordinates"""
        if self.is_touched():
            x_raw = self.read_touch(_GET_X)
            y_raw = self.read_touch(_GET_Y)
            
            # Calibration for landscape mode (90 degree rotation)
            x = int((x_raw - 300) * WIDTH / 3500)
            y = int((y_raw - 300) * HEIGHT / 3500)
            
            # Clamp to screen bounds
            x = max(0, min(WIDTH - 1, x))
            y = max(0, min(HEIGHT - 1, y))
            
            return x, y
        
        return 0, 0

    def test_display(self):
        """Test the display by filling it with yellow"""
        if self.display:
            print("Testing display fill...")
            self.display.clear(YELLOW)
            time.sleep(2)
            self.display.clear(BLACK)

    def get_dimensions(self):
        """Get display dimensions"""
        return WIDTH, HEIGHT

    def clear_screen(self, color=BLACK):
        """Clear the screen with specified color"""
        if self.display:
            self.display.clear(color)

    def set_backlight(self, state):
        """Control backlight on/off"""
        if self.backlight:
            self.backlight.value(1 if state else 0)


class TouchState:
    """Touch state tracking for click detection"""
    
    def __init__(self):
        self.last_touch_time = 0
        self.last_release_time = 0
        self.was_touched = False
        self.click_count = 0
        self.last_click_time = 0
        self.double_click_threshold = 500
        self.click_timeout = 300
        self.touch_threshold = 1000
        self.last_x = 0
        self.last_y = 0
        self.click_position_tolerance = 20
        
    def update(self, is_currently_touched, x, y, current_time):
        """Update touch state and detect clicks"""
        click_type = None
        
        if is_currently_touched and not self.was_touched:
            self.last_touch_time = current_time
            self.last_x = x
            self.last_y = y
            
        elif not is_currently_touched and self.was_touched:
            self.last_release_time = current_time
            touch_duration = current_time - self.last_touch_time
            
            if 50 < touch_duration < 1000:
                position_ok = True
                if self.click_count > 0:
                    distance = ((x - self.last_x) ** 2 + (y - self.last_y) ** 2) ** 0.5
                    position_ok = distance <= self.click_position_tolerance
                
                if position_ok:
                    time_since_last_click = current_time - self.last_click_time
                    
                    if self.click_count == 0 or time_since_last_click > self.double_click_threshold:
                        self.click_count = 1
                        self.last_click_time = current_time
                        
                    elif self.click_count == 1 and time_since_last_click <= self.double_click_threshold:
                        click_type = "double_click"
                        self.click_count = 0
                        self.last_click_time = 0
                else:
                    self.click_count = 1
                    self.last_click_time = current_time
        
        if self.click_count == 1:
            time_since_click = current_time - self.last_click_time
            if time_since_click > self.click_timeout:
                click_type = "single_click"
                self.click_count = 0
                self.last_click_time = 0
        
        self.was_touched = is_currently_touched
        return click_type
