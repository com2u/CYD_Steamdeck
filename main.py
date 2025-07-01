"""
ESP32-2432S028R (Cheap Yellow Display) Main Application
Refactored with modular structure using display.py and commands.py
"""
import network
import time
from display import DisplayManager, TouchState
from commands import CommandHandler
from audio import AudioManager


# WiFi credentials
WIFI_SSID = "Com2uRedmi11"
WIFI_PASSWORD = "SOMMERREGEN05"

def connect_wifi():
    """Connect to WiFi network"""
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    
    if not wlan.isconnected():
        print('Connecting to WiFi...')
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)
        
        # Wait for connection with timeout
        timeout = 10
        while not wlan.isconnected() and timeout > 0:
            time.sleep(1)
            timeout -= 1
            
    if wlan.isconnected():
        print('WiFi connected:', wlan.ifconfig())
        return True
    else:
        print('WiFi connection failed')
        return False

def main():
    print("=== ESP32 CYD Main Application ===")
    
    # Connect to WiFi
    wifi_connected = connect_wifi()
    
    # Initialize display manager
    display_manager = DisplayManager()
    display = display_manager.init_display()
    width, height = display_manager.get_dimensions()
    print(f"Display initialized: {width}x{height}")
    
    # Test the display
    display_manager.test_display()
    
    # Initialize touch
    spi_touch, touch_cs = display_manager.init_touch()
    print("Touch initialized")
    
    # Initialize audio manager
    audio_manager = AudioManager()
    audio_manager.init_speaker()
    
    # Play startup tone (A4 - 440Hz for 200ms)
    audio_manager.play_startup_tone()
    
    # Initialize touch state tracker
    touch_state = TouchState()
    
    # Initialize command handler
    command_handler = CommandHandler(display_manager, audio_manager)
    
    # Create button interface
    buttons = command_handler.create_button_interface()
    
    # Draw initial interface
    command_handler.draw_interface()
    
    print("Button interface ready")
    print("WiFi status:", "Connected" if wifi_connected else "Not Connected")

    
    # Main loop
    last_data_update = 0
    last_heartbeat = 0
    data_update_interval = 100  # Update system data every 100ms
    heartbeat_interval = 5000   # Send heartbeat every 5 seconds
    
    while True:
        current_time = time.ticks_ms()
        
        # Check touch using display manager
        is_currently_touched = display_manager.is_touched(touch_state.touch_threshold)
        x, y = display_manager.get_touch_coordinates()
        
        # Update touch state
        click_type = touch_state.update(is_currently_touched, x, y, current_time)
        
        # Handle touch events using command handler
        if is_currently_touched and not touch_state.was_touched:
            command_handler.handle_touch_down(x, y)
                
        elif not is_currently_touched and touch_state.was_touched:
            command_handler.handle_touch_up(x, y)
        
        elif is_currently_touched:
            command_handler.handle_touch_move(x, y)
        
        # Update system data from PC
        if time.ticks_diff(current_time, last_data_update) > data_update_interval:
            data_updated = command_handler.update_system_data()
            if data_updated:
                # Redraw interface to show updated data
                command_handler.draw_interface()
            last_data_update = current_time
        
        # Send heartbeat to PC
        if time.ticks_diff(current_time, last_heartbeat) > heartbeat_interval:
            command_handler.send_heartbeat()
            last_heartbeat = current_time
        
        time.sleep(0.05)

if __name__ == "__main__":
    main()
