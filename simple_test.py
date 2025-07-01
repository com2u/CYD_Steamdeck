"""
ESP32-2432S028R (Cheap Yellow Display) Simple Test
This application connects to WiFi and displays "Hello World"
"""
import network
import time
import machine
from machine import Pin, SPI
import ili9341

# Display pins for ESP32-2432S028R (Cheap Yellow Display)
TFT_CLK_PIN = 14
TFT_MOSI_PIN = 13
TFT_MISO_PIN = 12
TFT_CS_PIN = 15
TFT_DC_PIN = 2
TFT_RST_PIN = 4
TFT_BL_PIN = 21  # Backlight control

# Display dimensions
WIDTH = 320
HEIGHT = 240

# Colors
BLACK = 0x0000
WHITE = 0xFFFF
BLUE = 0x001F
RED = 0xF800
GREEN = 0x07E0

def connect_wifi():
    """Connect to WiFi network"""
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    
    print("Connecting to WiFi...")
    if not wlan.isconnected():
        wlan.connect('GPN-Open', '')  # SSID: GPN-Open, No password
        
        # Wait for connection with timeout
        max_wait = 20
        while max_wait > 0:
            if wlan.isconnected():
                break
            max_wait -= 1
            print("Waiting for connection...")
            time.sleep(1)
    
    if wlan.isconnected():
        print("Connected to WiFi")
        print("Network config:", wlan.ifconfig())
        return True
    else:
        print("Failed to connect to WiFi")
        return False

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
        w=WIDTH,
        h=HEIGHT,
        r=0)
    
    return display

def main():
    # Connect to WiFi
    wifi_connected = connect_wifi()
    
    # Initialize display
    display = init_display()
    
    # Clear the entire display
    display.clear()
    
    # Display Hello World
    display.fill(BLACK)
    display.text("Hello simple_test.py", 100, 20, WHITE)
    display.show()
    
    # Show WiFi status
    display.fill(BLACK)
    if wifi_connected:
        display.text("WiFi: Connected", 50, 20, GREEN)
    else:
        display.text("WiFi: Not Connected", 50, 20, RED)
    display.show_partial(30)
    
    # Show a message
    display.fill(BLACK)
    display.text("ESP32-2432S028R", 50, 20, BLUE)
    display.text("Simple Test", 50, 40, BLUE)
    display.show_partial(60)

if __name__ == "__main__":
    main()
