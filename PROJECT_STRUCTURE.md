# ESP32-2432S028R Project Structure

This document provides an overview of the project structure and how the components interact with each other.

## File Structure

```
ESP32-2432S028R/
├── boot.py              # Runs on startup, initializes system
├── main.py              # Main application code
├── ili9341.py           # Display driver
├── xpt2046.py           # Touchscreen driver
├── test.py              # Test utilities
├── pymakr.conf          # Pymakr configuration
├── README.md            # Project documentation
├── INSTALL.md           # Installation guide
└── PROJECT_STRUCTURE.md # This file
```

## Component Diagram

```mermaid
graph TD
    ESP32[ESP32-2432S028R] --> DISPLAY[ILI9341 Display]
    ESP32 --> TOUCH[XPT2046 Touchscreen]
    ESP32 --> WIFI[WiFi Module]
    
    BOOT[boot.py] --> MAIN[main.py]
    MAIN --> DISPLAY_DRIVER[ili9341.py]
    MAIN --> TOUCH_DRIVER[xpt2046.py]
    MAIN --> WIFI_CONNECT[WiFi Connection]
    
    DISPLAY_DRIVER --> DISPLAY
    TOUCH_DRIVER --> TOUCH
    WIFI_CONNECT --> WIFI
    
    TEST[test.py] -.-> DISPLAY_DRIVER
    TEST -.-> TOUCH_DRIVER
    TEST -.-> WIFI_CONNECT
```

## Data Flow

```mermaid
sequenceDiagram
    participant User
    participant ESP32
    participant Display
    participant Touch
    participant WiFi
    
    ESP32->>ESP32: Run boot.py
    ESP32->>ESP32: Run main.py
    ESP32->>WiFi: Connect to "GPN-Open"
    WiFi-->>ESP32: Connection status
    ESP32->>Display: Initialize
    ESP32->>Display: Show "Hello World"
    ESP32->>Display: Show WiFi status
    ESP32->>Touch: Initialize
    
    loop Touch Detection
        User->>Touch: Touch screen
        Touch-->>ESP32: Touch coordinates
        ESP32->>Display: Show coordinates
    end
```

## Pin Connections

### Display (ILI9341)

```
ESP32 Pin | ILI9341 Pin | Function
----------|-------------|----------
GPIO14    | SCK         | Clock
GPIO13    | MOSI        | Data Out
GPIO12    | MISO        | Data In
GPIO15    | CS          | Chip Select
GPIO2     | DC          | Data/Command
GPIO4     | RST         | Reset
GPIO21    | BL          | Backlight
```

### Touchscreen (XPT2046)

```
ESP32 Pin | XPT2046 Pin | Function
----------|-------------|----------
GPIO25    | SCK         | Clock
GPIO33    | MOSI        | Data Out
GPIO32    | MISO        | Data In
GPIO26    | CS          | Chip Select
```

## Software Components

### boot.py
- Initializes the system
- Sets CPU frequency
- Manages memory

### main.py
- Connects to WiFi
- Initializes display and touchscreen
- Displays "Hello World"
- Shows WiFi connection status
- Handles touch events and displays coordinates

### ili9341.py
- Driver for ILI9341 display
- Provides drawing functions (text, shapes, etc.)
- Manages display buffer

### xpt2046.py
- Driver for XPT2046 touchscreen
- Detects touch events
- Provides touch coordinates
- Handles calibration

### test.py
- Provides test functions for display, touchscreen, and WiFi
- Helps with debugging and verification

## Execution Flow

1. ESP32 boots and runs boot.py
2. boot.py initializes system and then runs main.py
3. main.py connects to WiFi network "GPN-Open"
4. main.py initializes the display and shows "Hello World"
5. main.py shows WiFi connection status
6. main.py initializes the touchscreen
7. When the screen is touched, main.py displays the touch coordinates
