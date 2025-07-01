"""
ESP32-2432S028R (Cheap Yellow Display) Final Application
This application connects to WiFi, displays "Hello World", and detects touch events
"""
import network
import time
import machine
from machine import Pin, SPI
import ili9341

    '''
    Display Pins:
    IO2 	TFT_RS 	AKA: TFT_DC
    IO12 	TFT_SDO 	AKA: TFT_MISO
    IO13 	TFT_SDI 	AKA: TFT_MOSI
    IO14 	TFT_SCK 	
    IO15 	TFT_CS 	
    IO21 	TFT_BL

    Touch Screen Pins:
    IO25 	XPT2046_CLK 	
    IO32 	XPT2046_MOSI 	
    IO33 	XPT2046_CS 	
    IO36 	XPT2046_IRQ 	
    IO39 	XPT2046_MISO
    '''

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
TOUCH_MISO_PIN = 39
TOUCH_MOSI_PIN = 32
TOUCH_CS_PIN = 33
TOUCH_IRQ_PIN = 36  # Optional interrupt pin

# XPT2046 Command bits
_GET_X = 0xD0  # X position (11010000)
_GET_Y = 0x90  # Y position (10010000)
_GET_Z1 = 0xB0  # Z1 position (10110000)
_GET_Z2 = 0xC0  # Z2 position (11000000)

# Display dimensions
WIDTH = 320
HEIGHT = 240

# Colors
BLACK = 0x0000
WHITE = 0xFFFF
BLUE = 0x001F
RED = 0xF800
GREEN = 0x07E0
YELLOW = 0xFFE0
CYAN = 0x07FF
MAGENTA = 0xF81F

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

def init_touch():
    """Initialize the touchscreen"""
    # Configure SPI for touch - use a separate SPI bus
    spi_touch = SPI(2, baudrate=1000000, 
                   sck=Pin(TOUCH_CLK_PIN),
                   mosi=Pin(TOUCH_MOSI_PIN),
                   miso=Pin(TOUCH_MISO_PIN))
    
    # Initialize touch CS pin
    touch_cs = Pin(TOUCH_CS_PIN, Pin.OUT)
    touch_cs.value(1)  # Deselect initially
    
    return spi_touch, touch_cs

def read_touch(spi, cs, command):
    """Read raw data from touch controller"""
    cs.value(0)  # Select touch controller
    
    # Send command and read response
    spi.write(bytes([command]))
    # Read 2 bytes (16 bits)
    data = bytearray(2)
    spi.readinto(data)
    
    cs.value(1)  # Deselect touch controller
    
    # Combine the bytes into a 12-bit value
    value = ((data[0] << 8) | data[1]) >> 3
    
    return value

def is_touched(spi, cs):
    """Check if the screen is being touched"""
    z1 = read_touch(spi, cs, _GET_Z1)
    z2 = read_touch(spi, cs, _GET_Z2)
    
    # Calculate touch pressure
    if z2 == 0:
        return False
        
    z = z1 + 4095 - z2
    
    return z > 1000  # Threshold for touch detection

def get_touch_coordinates(spi, cs):
    """Get touch coordinates"""
    # Read raw X, Y values
    raw_x = read_touch(spi, cs, _GET_X)
    raw_y = read_touch(spi, cs, _GET_Y)
    
    # Print raw values for debugging
    print(f"Raw X: {raw_x}, Raw Y: {raw_y}")
    
    # Return raw values for now
    return raw_x, raw_y

def main():
    # Connect to WiFi
    wifi_connected = connect_wifi()
    
    # Initialize display
    display = init_display()
    
    # Initialize touch
    spi_touch, touch_cs = init_touch()
    
    # Clear the entire display
    display.clear()
    
    # Display Hello World
    display.fill(BLACK)
    display.text("Hello finaly.py", 100, 20, WHITE)
    display.show()
    
    # Show WiFi status
    display.fill(BLACK)
    if wifi_connected:
        display.text("WiFi: Connected", 50, 20, GREEN)
    else:
        display.text("WiFi: Not Connected", 50, 20, RED)
    display.show_partial(30)
    
    # Show touch instructions
    display.fill(BLACK)
    display.text("Touch the screen", 50, 20, BLUE)
    display.show_partial(60)
    
    # Variables to track touch state
    touch_count = 0
    last_touch_time = 0
    touch_colors = [RED, GREEN, BLUE, YELLOW, CYAN, MAGENTA]
    
    # Main loop to handle touch events
    while True:
        current_time = time.time()
        
        # Check for touch
        if is_touched(spi_touch, touch_cs):
            # Get touch coordinates
            raw_x, raw_y = get_touch_coordinates(spi_touch, touch_cs)
            
            # Update display with touch information
            display.fill(BLACK)
            display.text("Touch detected!", 50, 20, WHITE)
            display.text(f"Raw X: {raw_x}", 50, 40, touch_colors[touch_count % len(touch_colors)])
            display.text(f"Raw Y: {raw_y}", 50, 60, touch_colors[touch_count % len(touch_colors)])
            display.show_partial(90)
            
            # Update touch count if it's been more than 1 second since last touch
            if current_time - last_touch_time > 1:
                touch_count += 1
                last_touch_time = current_time
            
            # Small delay to debounce
            time.sleep(0.1)

if __name__ == "__main__":
    main()
