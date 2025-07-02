"""
JSON Protocol Implementation for ESP32 CYD PC Service
Handles message serialization, parsing, and validation
"""
import json
import time
from typing import Dict, Any, Optional, Union
from config import JSON_INDENT, MAX_MESSAGE_LENGTH


class MessageType:
    """Message type constants"""
    COMMAND = "command"
    SYSTEM_DATA = "system_data"
    STATUS = "status"
    ACK = "ack"
    HEARTBEAT = "heartbeat"
    ERROR = "error"


class CommandType:
    """Command type constants"""
    INIT = "INIT"
    TEST = "TEST"
    EXIT = "EXIT"


class StatusType:
    """Status type constants"""
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    READY = "ready"
    ERROR = "error"


class JSONProtocol:
    """Handles JSON message protocol for ESP32 communication"""
    
    def __init__(self):
        self.message_delimiter = "\n"
    
    def create_system_data_message(self, system_data: Dict[str, Any]) -> str:
        """Create a system data message"""
        message = {
            "type": MessageType.SYSTEM_DATA,
            "timestamp": time.time(),
            "data": system_data
        }
        return self._serialize_message(message)
    
    def create_status_message(self, status: str, details: Optional[str] = None) -> str:
        """Create a status message"""
        message = {
            "type": MessageType.STATUS,
            "state": status,
            "timestamp": time.time()
        }
        if details:
            message["details"] = details
        return self._serialize_message(message)
    
    def create_ack_message(self, command: str, result: str, details: Optional[str] = None) -> str:
        """Create an acknowledgment message"""
        message = {
            "type": MessageType.ACK,
            "command": command,
            "result": result,
            "timestamp": time.time()
        }
        if details:
            message["details"] = details
        return self._serialize_message(message)
    
    def create_error_message(self, error_code: str, error_message: str) -> str:
        """Create an error message"""
        message = {
            "type": MessageType.ERROR,
            "error_code": error_code,
            "message": error_message,
            "timestamp": time.time()
        }
        return self._serialize_message(message)
    
    def parse_message(self, raw_message: str) -> Optional[Dict[str, Any]]:
        """
        Parse a JSON message from ESP32
        Returns None if not a valid JSON message
        """
        try:
            # Clean the message
            message = raw_message.strip()
            
            # Check if it looks like JSON
            if not (message.startswith('{') and message.endswith('}')):
                return None
            
            # Check message length
            if len(message) > MAX_MESSAGE_LENGTH:
                raise ValueError(f"Message too long: {len(message)} > {MAX_MESSAGE_LENGTH}")
            
            # Parse JSON
            parsed = json.loads(message)
            
            # Validate basic structure
            if not isinstance(parsed, dict):
                return None
            
            # Validate required fields
            if "type" not in parsed:
                return None
            
            return parsed
            
        except (json.JSONDecodeError, ValueError) as e:
            # Not a valid JSON message, probably debug output
            return None
    
    def validate_command_message(self, message: Dict[str, Any]) -> bool:
        """Validate a command message structure"""
        if message.get("type") != MessageType.COMMAND:
            return False
        
        required_fields = ["action", "timestamp"]
        return all(field in message for field in required_fields)
    
    def validate_heartbeat_message(self, message: Dict[str, Any]) -> bool:
        """Validate a heartbeat message structure"""
        if message.get("type") != MessageType.HEARTBEAT:
            return False
        
        required_fields = ["timestamp"]
        return all(field in message for field in required_fields)
    
    def is_valid_command(self, command: str) -> bool:
        """Check if command is valid"""
        valid_commands = [CommandType.INIT, CommandType.TEST, CommandType.EXIT]
        return command in valid_commands
    
    def _serialize_message(self, message: Dict[str, Any]) -> str:
        """Serialize message to JSON string"""
        try:
            json_str = json.dumps(message, indent=JSON_INDENT, separators=(',', ':'))
            return json_str + self.message_delimiter
        except (TypeError, ValueError) as e:
            raise ValueError(f"Failed to serialize message: {e}")
    
    def extract_command_info(self, message: Dict[str, Any]) -> tuple[str, float]:
        """Extract command and timestamp from command message"""
        if not self.validate_command_message(message):
            raise ValueError("Invalid command message")
        
        return message["action"], message["timestamp"]
    
    def is_json_line(self, line: str) -> bool:
        """Quick check if a line might be JSON"""
        stripped = line.strip()
        return stripped.startswith('{') and stripped.endswith('}')


# Global protocol instance
protocol = JSONProtocol()


def create_system_data_message(system_data: Dict[str, Any]) -> str:
    """Convenience function to create system data message"""
    return protocol.create_system_data_message(system_data)


def create_status_message(status: str, details: Optional[str] = None) -> str:
    """Convenience function to create status message"""
    return protocol.create_status_message(status, details)


def create_ack_message(command: str, result: str, details: Optional[str] = None) -> str:
    """Convenience function to create ack message"""
    return protocol.create_ack_message(command, result, details)


def parse_message(raw_message: str) -> Optional[Dict[str, Any]]:
    """Convenience function to parse message"""
    return protocol.parse_message(raw_message)


def is_json_line(line: str) -> bool:
    """Convenience function to check if line is JSON"""
    return protocol.is_json_line(line)
