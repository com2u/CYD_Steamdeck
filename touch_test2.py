"""
Touchscreen test for ESP32-2432S028R with alternative pin configurations
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

# Alternative touch pin configurations to try
# Configuration 2 - Alternative 1
TOUCH_CLK_PIN_2 = 25
TOUCH_MISO_PIN_2 = 39  # Changed from 32
TOUCH_MOSI_PIN_2 = 33
TOUCH_CS_PIN_2 = 26

# Configuration 3 - Alternative 2
TOUCH_CLK_PIN_3 = 25
TOUCH_MISO_PIN_3 = 32
TOUCH_MOSI_PIN_3 = 33
TOUCH_CS_PIN_3 = 27  # Changed from 26

# Configuration 4 - Alternative 3 (using same SPI as display)
TOUCH_CLK_PIN_4 = 14  # Same as display
TOUCH_MISO_PIN_4 = 12  # Same as display
TOUCH_MOSI_PIN_4 = 13  # Same as display
TOUCH_CS_PIN_4 = 26  # Different CS pin

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

def test_touch_config(config_num, clk_pin, miso_pin, mosi_pin, cs_pin):
    """Test touchscreen with the specified configuration"""
    print(f"Testing touchscreen with configuration {config_num}...")
    
    # Initialize display
    display = init_display()
    display.clear()
    
    # Display test info
    display.fill(BLACK)
    display.text(f"Touch Test - Config {config_num}", 70, 10, WHITE)
    display.show()
    
    # Show pin configuration
    display.fill(BLACK)
    display.text(f"CLK: {clk_pin}, MISO: {miso_pin}", 60, 10, WHITE)
    display.text(f"MOSI: {mosi_pin}, CS: {cs_pin}", 60, 20, WHITE)
    display.show_partial(30)
    
    try:
        # Configure SPI for touch
        if config_num == 4:
            # Use the same SPI as the display
            spi_touch = SPI(1, baudrate=1000000, sck=Pin(clk_pin), mosi=Pin(mosi_pin))
        else:
            # Use a separate SPI
            spi_touch = SPI(2, baudrate=1000000, sck=Pin(clk_pin), mosi=Pin(mosi_pin), miso=Pin(miso_pin))
        
        # Initialize touch controller
        touch_cs = Pin(cs_pin, Pin.OUT)
        touch = XPT2046(spi_touch, cs=touch_cs, half_duplex=(config_num == 4))
        
        # Calibrate touch
        touch.calibrate(320, 240)
        
        # Show instructions
        display.fill(BLACK)
        display.text("Touch the screen", 90, 10, GREEN)
        display.show_partial(60)
        
        # Test touch for 15 seconds
        end_time = time.time() + 15
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
        
        # Show test result
        display.fill(BLACK)
        if touch_count > 0:
            display.text(f"Config {config_num}: SUCCESS", 70, 10, GREEN)
            display.text(f"Detected {touch_count} touches", 70, 20, GREEN)
        else:
            display.text(f"Config {config_num}: FAILED", 70, 10, RED)
            display.text("No touches detected", 70, 20, RED)
        display.show_partial(90)
        time.sleep(3)
        
        print(f"Touch test for config {config_num} complete")
        return touch_count > 0
        
    except Exception as e:
        # Display error
        display.fill(BLACK)
        display.text(f"Config {config_num}: ERROR", 70, 10, RED)
        display.text(str(e)[:30], 10, 20, RED)
        display.show_partial(90)
        time.sleep(3)
        
        print(f"Error in config {config_num}: {e}")
        return False

def main():
    # Test all configurations
    print("Testing all touch configurations...")
    
    # Test configuration 2
    success2 = test_touch_config(2, TOUCH_CLK_PIN_2, TOUCH_MISO_PIN_2, TOUCH_MOSI_PIN_2, TOUCH_CS_PIN_2)
    
    # Test configuration 3
    success3 = test_touch_config(3, TOUCH_CLK_PIN_3, TOUCH_MISO_PIN_3, TOUCH_MOSI_PIN_3, TOUCH_CS_PIN_3)
    
    # Test configuration 4
    success4 = test_touch_config(4, TOUCH_CLK_PIN_4, TOUCH_MISO_PIN_4, TOUCH_MOSI_PIN_4, TOUCH_CS_PIN_4)
    
    # Initialize display for final results
    display = init_display()
    display.clear()
    
    # Show final results
    display.fill(BLACK)
    display.text("Touch Test Results:", 80, 10, WHITE)
    display.show()
    
    display.fill(BLACK)
    display.text(f"Config 2: {'SUCCESS' if success2 else 'FAILED'}", 60, 10, GREEN if success2 else RED)
    display.show_partial(30)
    
    display.fill(BLACK)
    display.text(f"Config 3: {'SUCCESS' if success3 else 'FAILED'}", 60, 10, GREEN if success3 else RED)
    display.show_partial(60)
    
    display.fill(BLACK)
    display.text(f"Config 4: {'SUCCESS' if success4 else 'FAILED'}", 60, 10, GREEN if success4 else RED)
    display.show_partial(90)
    
    print("All touch tests complete")

if __name__ == "__main__":
    main()
