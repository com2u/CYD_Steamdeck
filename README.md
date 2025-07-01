# ESP32-2432S028R (Cheap Yellow Display) MicroPython Project

This project provides MicroPython code for the ESP32-2432S028R development board, also known as the "Cheap Yellow Display". It includes code for connecting to WiFi, displaying text on the LCD, and handling touch input.

## Hardware

- ESP32-2432S028R board with:
  - ESP32 microcontroller
  - 2.8" 320x240 LCD display (ILI9341 controller)
  - XPT2046 touch controller
  - Various GPIO pins for interfacing

## Files

- `boot.py`: Initial boot script that runs when the ESP32 starts up
- `main.py`: Main application that runs after boot.py
- `ili9341.py`: Driver for the ILI9341 LCD controller
- `xpt2046.py`: Driver for the XPT2046 touch controller
- `test.py`: Basic test script for the display
- `touch_test.py`: Basic test script for the touchscreen
- `touch_test2.py`: Alternative test script for the touchscreen
- `touch_raw_test.py`: Raw touchscreen test that displays raw touch values
- `simple_test.py`: Simple test that displays "Hello World" and connects to WiFi
- `final.py`: Final application that connects to WiFi, displays "Hello World", and detects touch events

## Usage

### Uploading Files

Use the provided upload scripts to upload the files to your ESP32:

- Windows: `upload.bat`
- Linux/Mac: `upload.sh`

Make sure to set the correct COM port in the script before running it.

### Running Different Applications

The ESP32 will automatically run `boot.py` followed by `main.py` when it starts up. You have several options to run different applications:

1. **Run directly**: Use the provided scripts to run a specific application:
   - Windows: `run_final.bat`
   - Linux/Mac: `run_final.sh`

2. **Set as default**: Make `final.py` the default application that runs on startup:
   - Windows: `set_final_as_main.bat`
   - Linux/Mac: `set_final_as_main.sh`

3. **Use REPL**: Connect to the ESP32's REPL and import the script:
   ```python
   import final  # Run the final application
   ```

### WiFi Configuration

The code is configured to connect to a WiFi network named "GPN-Open" with no password. To use a different WiFi network, modify the `connect_wifi()` function in the script you're using.

### Touch Calibration

The touchscreen may require calibration for accurate coordinate mapping. The current implementation displays raw touch values, which can be used for debugging.

## Troubleshooting

- If the display doesn't work, check the pin connections and make sure the display is properly powered.
- If the touchscreen doesn't work, try different SPI configurations and command bytes.
- If the WiFi connection fails, check your network settings and make sure the ESP32 is within range of the access point.

## License

This project is open source and available under the MIT License.
