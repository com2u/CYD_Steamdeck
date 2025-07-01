"""
Touchscreen test for ESP32-2432S028R
"""

import time
import machine
from machine import Pin, SPI
import ili9341
from xpt2046 import XPT2046

# Display pins for ESP32-2432S028R
TFT_CLK_PIN = 14
TFT_MOSI_PIN = 13
TFT_MISO_PIN = 12
TFT_CS_PIN = 15
TFT_DC_PIN = 2
TFT_RST_PIN = 4
TFT_BL_PIN = 21  # Backlight control

# Touch pins - try different configurations
# Configuration 1 - Original
TOUCH_CLK_PIN = 25
TOUCH_MISO_PIN = 32
TOUCH_MOSI_PIN = 33
TOUCH_CS_PIN = 26

# Colors
BLACK = 0x0000
WHITE = 0xFFFF
BLUE = 0x001F
RED = 0xF800
GREEN = 0x07E0

def init_display():
    """Initialize the display"""
    # Configure SPI for display
    spi_tft = SPI(1, baudrate=40000000, sck=Pin(TFT_CLK_PIN), mosi=Pin(TFT_MOSI_PIN))
    
    # Configure display pins
    display_cs = Pin(TFT_CS_PIN, Pin.OUT)
    display_dc = Pin(TFT_DC_PIN, Pin.OUT)
    display_rst = Pin(TFT_RST_PIN, Pin.OUT)
    
    # Initialize backlight
    backlight = Pin(TFT_BL_PIN, Pin.OUT)
    backlight.value(1)  # Turn on backlight
    
    # Initialize display
    display = ili9341.ILI9341(
        spi_tft,
        cs=display_cs,
        dc=display_dc,
        rst=display_rst,
        w=320,
        h=240,
        r=0)
    
    return display

def test_touch_config1():
    """Test touchscreen with configuration 1"""
    print("Testing touchscreen with configuration 1...")
    
    # Initialize display
    display = init_display()
    display.clear()
    
    # Display test info
    display.fill(BLACK)
    display.text("Touch Test - Config 1", 80, 10, WHITE)
    display.show()
    
    # Configure SPI for touch
    spi_touch = SPI(2, baudrate=1000000, 
                   sck=Pin(TOUCH_CLK_PIN),
                   mosi=Pin(TOUCH_MOSI_PIN),
                   miso=Pin(TOUCH_MISO_PIN))
    
    # Initialize touch controller
    touch_cs = Pin(TOUCH_CS_PIN, Pin.OUT)
    touch = XPT2046(spi_touch, cs=touch_cs)
    
    # Calibrate touch
    touch.calibrate(320, 240)
    
    # Show instructions
    display.fill(BLACK)
    display.text("Touch the screen", 90, 10, GREEN)
    display.show_partial(30)
    
    # Test touch for 30 seconds
    end_time = time.time() + 30
    touch_count = 0
    
    while time.time() < end_time:
        if touch.touched():
            touch_count += 1
            x, y = touch.get_xy()
            
            # Display coordinates
            display.fill(BLACK)
            display.text(f"Touch: x={x}, y={y}", 80, 10, WHITE)
            display.text(f"Count: {touch_count}", 80, 20, BLUE)
            display.show_partial(60)
            
            # Small delay to debounce
            time.sleep(0.1)
    
    print("Touch test complete")

def main():
    # Test configuration 1
    test_touch_config1()

if __name__ == "__main__":
    main()
