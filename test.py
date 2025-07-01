"""
Test script for ESP32-2432S028R (Cheap Yellow Display)
This script provides simple tests for the display and touchscreen
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
TFT_RST_PIN = 4  # Changed from 12 to 4 to avoid conflict with MISO
TFT_BL_PIN = 21  # Backlight control

# Touch pins
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
CYAN = 0x07FF
MAGENTA = 0xF81F
YELLOW = 0xFFE0

def test_display():
    """Test the display functionality"""
    print("Testing display...")
    
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
    
    # Clear the display
    display.clear()
    time.sleep(1)
    
    # Display test pattern - RED
    display.fill(RED)
    display.text("Display Test", 100, 20, WHITE)
    display.show()
    
    display.fill(RED)
    display.text("RED", 140, 20, WHITE)
    display.show_partial(30)
    time.sleep(1)
    
    # Display test pattern - GREEN
    display.fill(GREEN)
    display.text("Display Test", 100, 20, BLACK)
    display.show()
    
    display.fill(GREEN)
    display.text("GREEN", 130, 20, BLACK)
    display.show_partial(30)
    time.sleep(1)
    
    # Display test pattern - BLUE
    display.fill(BLUE)
    display.text("Display Test", 100, 20, WHITE)
    display.show()
    
    display.fill(BLUE)
    display.text("BLUE", 135, 20, WHITE)
    display.show_partial(30)
    time.sleep(1)
    
    # Draw test pattern in sections
    display.clear()
    
    # First row of rectangles
    display.fill(BLACK)
    display.fill_rect(0, 0, 80, 30, RED)
    display.fill_rect(80, 0, 80, 30, GREEN)
    display.fill_rect(160, 0, 80, 30, BLUE)
    display.fill_rect(240, 0, 80, 30, CYAN)
    display.show()
    
    # Second row of rectangles
    display.fill(BLACK)
    display.fill_rect(0, 0, 80, 30, MAGENTA)
    display.fill_rect(80, 0, 80, 30, YELLOW)
    display.fill_rect(160, 0, 80, 30, WHITE)
    display.fill_rect(240, 0, 80, 30, BLACK)
    display.show_partial(30)
    
    # Draw lines in third section
    display.fill(BLACK)
    for i in range(0, 320, 20):
        display.line(0, 0, i, 30, WHITE)
    display.show_partial(60)
    
    # Display completion message in fourth section
    display.fill(BLACK)
    display.text("Display Test Complete", 80, 20, WHITE)
    display.show_partial(90)
    
    print("Display test complete")
    return display

def test_touch(display=None):
    """Test the touchscreen functionality"""
    print("Testing touchscreen...")
    
    # If no display is provided, initialize one
    if display is None:
        display = test_display()
    
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
    
    # Clear display and show touch test instructions
    display.clear()
    
    display.fill(BLACK)
    display.text("Touch Test", 120, 20, WHITE)
    display.show()
    
    display.fill(BLACK)
    display.text("Touch the screen", 90, 20, WHITE)
    display.show_partial(30)
    
    # Test touch for 30 seconds
    end_time = time.time() + 30
    last_x, last_y = 0, 0
    
    while time.time() < end_time:
        if touch.touched():
            x, y = touch.get_xy()
            
            # Only update if position changed
            if x != last_x or y != last_y:
                # Display new coordinates in third section
                display.fill(BLACK)
                display.text(f"Touch: x={x}, y={y}", 90, 20, WHITE)
                display.show_partial(60)
                
                # Draw a small dot indicator in fourth section
                display.fill(BLACK)
                # We can't draw directly at touch position due to buffer limitations
                # So we'll just show a message about where the touch was detected
                display.text(f"Touched at ({x},{y})", 80, 20, RED)
                display.show_partial(90)
                
                last_x, last_y = x, y
            
            # Small delay to debounce
            time.sleep(0.1)
    
    display.clear()
    display.fill(BLACK)
    display.text("Touch Test Complete", 80, 20, WHITE)
    display.show()
    
    print("Touchscreen test complete")

def test_wifi():
    """Test WiFi connectivity"""
    import network
    
    print("Testing WiFi...")
    
    # Initialize display for status
    spi_tft = SPI(1, baudrate=40000000, sck=Pin(TFT_CLK_PIN), mosi=Pin(TFT_MOSI_PIN))
    display_cs = Pin(TFT_CS_PIN, Pin.OUT)
    display_dc = Pin(TFT_DC_PIN, Pin.OUT)
    display_rst = Pin(TFT_RST_PIN, Pin.OUT)
    backlight = Pin(TFT_BL_PIN, Pin.OUT)
    backlight.value(1)
    
    display = ili9341.ILI9341(
        spi_tft,
        cs=display_cs,
        dc=display_dc,
        rst=display_rst,
        w=320,
        h=240,
        r=0)
    
    display.clear()
    
    display.fill(BLACK)
    display.text("WiFi Test", 120, 20, WHITE)
    display.show()
    
    display.fill(BLACK)
    display.text("Connecting to GPN-Open...", 60, 20, WHITE)
    display.show_partial(30)
    
    # Connect to WiFi
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    
    if not wlan.isconnected():
        wlan.connect('GPN-Open', '')  # SSID: GPN-Open, No password
        
        # Wait for connection with timeout
        max_wait = 20
        while max_wait > 0:
            if wlan.isconnected():
                break
            max_wait -= 1
            display.fill(BLACK)
            display.text(f"Waiting... {max_wait}", 100, 20, YELLOW)
            display.show_partial(60)
            time.sleep(1)
    
    # Display result
    if wlan.isconnected():
        ip, subnet, gateway, dns = wlan.ifconfig()
        
        display.fill(BLACK)
        display.text("Connected!", 120, 20, GREEN)
        display.show_partial(60)
        
        display.fill(BLACK)
        display.text(f"IP: {ip}", 80, 20, WHITE)
        display.show_partial(90)
        
        display.fill(BLACK)
        display.text(f"Gateway: {gateway}", 80, 20, WHITE)
        display.show_partial(120)
        
        print("WiFi connected")
        print("IP:", ip)
    else:
        display.fill(BLACK)
        display.text("Connection Failed", 90, 20, RED)
        display.show_partial(60)
        print("WiFi connection failed")
    time.sleep(5)
    
    print("WiFi test complete")
    return display

def run_all_tests():
    """Run all tests sequentially"""
    print("Running all tests...")
    
    # Test WiFi first
    display = test_wifi()
    time.sleep(2)
    
    # Test display
    display = test_display()
    time.sleep(2)
    
    # Test touchscreen
    test_touch(display)
    
    print("All tests completed")

if __name__ == "__main__":
    # Uncomment the test you want to run
    # test_display()
    # test_touch()
    # test_wifi()
    run_all_tests()  # Run all tests
