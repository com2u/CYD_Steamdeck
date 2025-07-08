"""
Raw touchscreen test for ESP32-2432S028R
This script tests direct communication with the XPT2046 touch controller
"""

import time
import machine
from machine import Pin, SPI
import ili9341

# Display pins for ESP32-2432S028R
TFT_CLK_PIN = 14
TFT_MOSI_PIN = 13
TFT_MISO_PIN = 12
TFT_CS_PIN = 15
TFT_DC_PIN = 2
TFT_RST_PIN = 4
TFT_BL_PIN = 21  # Backlight control

# Touch pins - standard configuration for ESP32-2432S028R
TOUCH_CLK_PIN = 25
TOUCH_MISO_PIN = 32
TOUCH_MOSI_PIN = 33
TOUCH_CS_PIN = 26
TOUCH_IRQ_PIN = 36  # Optional interrupt pin

# XPT2046 Command bits - try original commands
_GET_X = 0xD0  # X position - Original 0xD0 (11010000)
_GET_Y = 0x90  # Y position - Original 0x90 (10010000)
_GET_Z1 = 0xB0  # Z1 position
_GET_Z2 = 0xC0  # Z2 position

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

def read_touch_raw(spi, cs, command):
    """Read raw data from touch controller
    
    Args:
        spi: SPI bus instance
        cs: Chip select pin
        command: Command byte
        
    Returns:
        int: 12-bit response value
    """
    cs.value(0)  # Select touch controller
    
    # Simpler approach: send command and read response separately
    spi.write(bytes([command]))
    # Read 2 bytes (16 bits)
    data = bytearray(2)
    spi.readinto(data)
    
    cs.value(1)  # Deselect touch controller
    
    # Combine the bytes into a 12-bit value
    value = ((data[0] << 8) | data[1]) >> 3
    
    return value

def test_touch_raw():
    """Test raw communication with touchscreen"""
    print("Testing raw touchscreen communication...")
    
    # Initialize display
    display = init_display()
    display.clear()
    
    # Display test info
    display.fill(BLACK)
    display.text("Raw Touch Test", 90, 10, WHITE)
    display.show()
    
    # Use the same SPI bus as the display
    spi_touch = SPI(1, baudrate=1000000, 
                   sck=Pin(TFT_CLK_PIN),
                   mosi=Pin(TFT_MOSI_PIN),
                   miso=Pin(TFT_MISO_PIN))
    
    # Initialize touch CS pin
    touch_cs = Pin(TOUCH_CS_PIN, Pin.OUT)
    touch_cs.value(1)  # Deselect initially
    
    # Initialize interrupt pin if available
    if TOUCH_IRQ_PIN:
        touch_irq = Pin(TOUCH_IRQ_PIN, Pin.IN)
    else:
        touch_irq = None
    
    # Show instructions
    display.fill(BLACK)
    display.text("Touch the screen", 90, 10, GREEN)
    display.show_partial(30)
    
    # Test touch for 30 seconds
    end_time = time.time() + 30
    
    while time.time() < end_time:
        # Check if touch is pressed (using IRQ pin if available)
        touch_pressed = False
        if touch_irq:
            touch_pressed = not touch_irq.value()  # IRQ is active low
        
        # If no IRQ pin or IRQ indicates touch, read touch data
        if not touch_irq or touch_pressed:
            # Read raw X, Y values
            x_raw = read_touch_raw(spi_touch, touch_cs, _GET_X)
            y_raw = read_touch_raw(spi_touch, touch_cs, _GET_Y)
            z1_raw = read_touch_raw(spi_touch, touch_cs, _GET_Z1)
            z2_raw = read_touch_raw(spi_touch, touch_cs, _GET_Z2)
            
            # Calculate pressure
            pressure = 0
            if z2_raw != 0:
                pressure = z1_raw + 4095 - z2_raw
            
            # Display raw values
            display.fill(BLACK)
            display.text(f"X: {x_raw}", 80, 10, WHITE)
            display.text(f"Y: {y_raw}", 80, 20, WHITE)
            display.show_partial(30)
            
            display.fill(BLACK)
            display.text(f"Z1: {z1_raw}", 80, 10, BLUE)
            display.text(f"Z2: {z2_raw}", 80, 20, BLUE)
            display.text(f"P: {pressure}", 80, 30, BLUE)
            display.show_partial(60)
            
            # Small delay to debounce
            time.sleep(0.1)
    
    print("Raw touch test complete")

def main():
    test_touch_raw()

# Run the main function automatically when imported
main()
