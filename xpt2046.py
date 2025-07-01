"""
XPT2046 Touch Screen Driver for MicroPython
"""

import time
from micropython import const

# XPT2046 Command bits
_GET_X = const(0b11010000)  # X position
_GET_Y = const(0b10010000)  # Y position
_GET_Z1 = const(0b10110000)  # Z1 position
_GET_Z2 = const(0b11000000)  # Z2 position

# Touch detection threshold
TOUCH_THRESHOLD = const(1000)

class XPT2046:
    """
    Driver for XPT2046 touch controller
    """
    def __init__(self, spi, cs, int_pin=None, half_duplex=True, 
                 cal_x1=0, cal_y1=0, cal_x2=4095, cal_y2=4095):
        """
        Initialize the touch screen controller
        
        Args:
            spi: SPI bus instance
            cs: Chip select pin
            int_pin: Interrupt pin (optional)
            half_duplex: Whether to use half-duplex SPI communication
            cal_x1, cal_y1, cal_x2, cal_y2: Calibration values
        """
        self.spi = spi
        self.cs = cs
        self.int_pin = int_pin
        self.half_duplex = half_duplex
        
        # Default calibration values
        self.cal_x1 = cal_x1
        self.cal_y1 = cal_y1
        self.cal_x2 = cal_x2
        self.cal_y2 = cal_y2
        
        # Screen dimensions for calibration
        self.width = 320
        self.height = 240
        
        # Initialize CS pin
        self.cs.value(1)
        
        # Initialize interrupt pin if provided
        if self.int_pin:
            self.int_pin.init(self.int_pin.IN)
    
    def calibrate(self, width=None, height=None):
        """
        Set the calibration parameters
        
        Args:
            width: Screen width (optional)
            height: Screen height (optional)
        """
        if width is not None:
            self.width = width
        if height is not None:
            self.height = height
    
    def _send_command(self, command):
        """
        Send a command to the touch controller and read the response
        
        Args:
            command: Command byte
            
        Returns:
            int: 12-bit response value
        """
        self.cs.value(0)
        
        # Simpler approach that works with both half and full duplex
        self.spi.write(bytes([command]))
        # Read 2 bytes (16 bits)
        data = bytearray(2)
        self.spi.readinto(data)
        
        self.cs.value(1)
        
        # Combine the bytes into a 12-bit value
        return ((data[0] << 8) | data[1]) >> 3
    
    def _raw_x(self):
        """Read raw X position"""
        return self._send_command(_GET_Y)  # Swapped to use Y command for X
    
    def _raw_y(self):
        """Read raw Y position"""
        return self._send_command(_GET_X)  # Swapped to use X command for Y
    
    def _raw_z1(self):
        """Read raw Z1 position (pressure)"""
        return self._send_command(_GET_Z1)
    
    def _raw_z2(self):
        """Read raw Z2 position (pressure)"""
        return self._send_command(_GET_Z2)
    
    def touched(self):
        """
        Check if the screen is being touched
        
        Returns:
            bool: True if touched, False otherwise
        """
        if self.int_pin:
            # If interrupt pin is provided, use it for touch detection
            return not self.int_pin.value()
        else:
            # Otherwise, use pressure reading
            z1 = self._raw_z1()
            z2 = self._raw_z2()
            
            # Calculate touch pressure
            if z2 == 0:
                return False
                
            z = z1 + 4095 - z2
            
            return z > TOUCH_THRESHOLD
    
    def get_raw_xy(self):
        """
        Get raw touch coordinates
        
        Returns:
            tuple: (x, y) raw touch coordinates
        """
        x = self._raw_x()
        y = self._raw_y()
        return x, y
    
    def get_xy(self):
        """
        Get calibrated touch coordinates
        
        Returns:
            tuple: (x, y) calibrated touch coordinates
        """
        raw_x, raw_y = self.get_raw_xy()
        
        # Debug print to see raw values
        print(f"Raw X: {raw_x}, Raw Y: {raw_y}")
        
        # Simple scaling with inversion for both axes
        x = self.width - 1 - int(raw_x * self.width / 4095)
        y = self.height - 1 - int(raw_y * self.height / 4095)
        
        # Ensure coordinates are within screen bounds
        x = max(0, min(x, self.width - 1))
        y = max(0, min(y, self.height - 1))
        
        return x, y
