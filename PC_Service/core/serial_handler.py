"""
Serial Handler for ESP32 CYD PC Service
Manages robust serial communication with automatic reconnection
"""
import serial
import threading
import time
import queue
from typing import Optional, Callable, Any
from config import (
    DEFAULT_SERIAL_PORT, BAUD_RATE, SERIAL_TIMEOUT, 
    RECONNECT_DELAY, MAX_RECONNECT_ATTEMPTS
)


class SerialHandler:
    """Handles serial communication with ESP32 with robust reconnection"""
    
    def __init__(self, port: str = DEFAULT_SERIAL_PORT, 
                 on_message_received: Optional[Callable[[str], None]] = None,
                 on_connection_changed: Optional[Callable[[bool], None]] = None):
        self.port = port
        self.baud_rate = BAUD_RATE
        self.timeout = SERIAL_TIMEOUT
        self.reconnect_delay = RECONNECT_DELAY
        self.max_reconnect_attempts = MAX_RECONNECT_ATTEMPTS
        
        # Callbacks
        self.on_message_received = on_message_received
        self.on_connection_changed = on_connection_changed
        
        # Serial connection
        self.serial_connection: Optional[serial.Serial] = None
        self.is_connected = False
        
        # Threading
        self.read_thread: Optional[threading.Thread] = None
        self.write_queue = queue.Queue()
        self.write_thread: Optional[threading.Thread] = None
        self.running = False
        
        # Statistics
        self.messages_sent = 0
        self.messages_received = 0
        self.connection_attempts = 0
        self.last_connection_time = None
        
    def start(self) -> bool:
        """Start the serial handler"""
        if self.running:
            return True
            
        print(f"Starting serial handler on {self.port}...")
        self.running = True
        
        # Start threads
        self.read_thread = threading.Thread(target=self._read_loop, daemon=True)
        self.write_thread = threading.Thread(target=self._write_loop, daemon=True)
        
        self.read_thread.start()
        self.write_thread.start()
        
        # Try initial connection
        return self._connect()
    
    def stop(self):
        """Stop the serial handler"""
        print("Stopping serial handler...")
        self.running = False
        
        # Disconnect
        self._disconnect()
        
        # Wait for threads to finish
        if self.read_thread and self.read_thread.is_alive():
            self.read_thread.join(timeout=2.0)
        if self.write_thread and self.write_thread.is_alive():
            self.write_thread.join(timeout=2.0)
    
    def send_message(self, message: str) -> bool:
        """Queue a message to be sent"""
        if not self.running:
            return False
            
        try:
            self.write_queue.put(message, timeout=1.0)
            return True
        except queue.Full:
            print("Write queue is full, dropping message")
            return False
    
    def _connect(self) -> bool:
        """Attempt to connect to the serial port"""
        try:
            if self.serial_connection and self.serial_connection.is_open:
                return True
                
            print(f"Attempting to connect to {self.port}...")
            self.connection_attempts += 1
            
            self.serial_connection = serial.Serial(
                port=self.port,
                baudrate=self.baud_rate,
                timeout=self.timeout,
                write_timeout=self.timeout
            )
            
            if self.serial_connection.is_open:
                self.is_connected = True
                self.last_connection_time = time.time()
                print(f"Connected to {self.port}")
                
                # Notify connection change
                if self.on_connection_changed:
                    self.on_connection_changed(True)
                
                return True
            else:
                print(f"Failed to open {self.port}")
                return False
                
        except serial.SerialException as e:
            print(f"Serial connection error: {e}")
            return False
        except Exception as e:
            print(f"Unexpected error connecting to {self.port}: {e}")
            return False
    
    def _disconnect(self):
        """Disconnect from the serial port"""
        if self.serial_connection:
            try:
                if self.serial_connection.is_open:
                    self.serial_connection.close()
                    print(f"Disconnected from {self.port}")
            except Exception as e:
                print(f"Error closing serial connection: {e}")
            finally:
                self.serial_connection = None
                
        if self.is_connected:
            self.is_connected = False
            # Notify connection change
            if self.on_connection_changed:
                self.on_connection_changed(False)
    
    def _read_loop(self):
        """Main read loop running in separate thread"""
        reconnect_attempts = 0
        
        while self.running:
            if not self.is_connected:
                # Try to reconnect
                if self.max_reconnect_attempts == 0 or reconnect_attempts < self.max_reconnect_attempts:
                    if self._connect():
                        reconnect_attempts = 0
                    else:
                        reconnect_attempts += 1
                        print(f"Reconnection attempt {reconnect_attempts} failed")
                        time.sleep(self.reconnect_delay)
                else:
                    print(f"Max reconnection attempts ({self.max_reconnect_attempts}) reached")
                    time.sleep(self.reconnect_delay * 2)
                continue
            
            try:
                if self.serial_connection and self.serial_connection.is_open:
                    # Check if data is available
                    if self.serial_connection.in_waiting > 0:
                        line = self.serial_connection.readline().decode('utf-8', errors='ignore').strip()
                        if line:
                            self.messages_received += 1
                            if self.on_message_received:
                                self.on_message_received(line)
                    else:
                        # Small delay to prevent busy waiting
                        time.sleep(0.01)
                else:
                    self._disconnect()
                    
            except serial.SerialException as e:
                print(f"Serial read error: {e}")
                self._disconnect()
                reconnect_attempts = 0
            except Exception as e:
                print(f"Unexpected read error: {e}")
                time.sleep(0.1)
    
    def _write_loop(self):
        """Main write loop running in separate thread"""
        while self.running:
            try:
                # Get message from queue with timeout
                message = self.write_queue.get(timeout=0.1)
                
                if self.is_connected and self.serial_connection and self.serial_connection.is_open:
                    try:
                        # Ensure message ends with newline
                        if not message.endswith('\n'):
                            message += '\n'
                            
                        self.serial_connection.write(message.encode('utf-8'))
                        self.serial_connection.flush()
                        self.messages_sent += 1
                        
                    except serial.SerialException as e:
                        print(f"Serial write error: {e}")
                        self._disconnect()
                        # Put message back in queue to retry
                        self.write_queue.put(message)
                    except Exception as e:
                        print(f"Unexpected write error: {e}")
                else:
                    # Not connected, put message back in queue
                    self.write_queue.put(message)
                    time.sleep(0.1)
                    
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Write loop error: {e}")
                time.sleep(0.1)
    
    def get_status(self) -> dict:
        """Get connection status and statistics"""
        return {
            "connected": self.is_connected,
            "port": self.port,
            "messages_sent": self.messages_sent,
            "messages_received": self.messages_received,
            "connection_attempts": self.connection_attempts,
            "last_connection_time": self.last_connection_time,
            "queue_size": self.write_queue.qsize()
        }
    
    def change_port(self, new_port: str) -> bool:
        """Change the serial port"""
        if new_port == self.port:
            return True
            
        print(f"Changing port from {self.port} to {new_port}")
        
        # Disconnect current connection
        self._disconnect()
        
        # Update port
        self.port = new_port
        
        # Try to connect to new port
        return self._connect()


def create_serial_handler(port: str = DEFAULT_SERIAL_PORT,
                         on_message_received: Optional[Callable[[str], None]] = None,
                         on_connection_changed: Optional[Callable[[bool], None]] = None) -> SerialHandler:
    """Factory function to create a serial handler"""
    return SerialHandler(port, on_message_received, on_connection_changed)
