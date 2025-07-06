"""
JSON Protocol Implementation for ESP32 CYD
Lightweight JSON handling using ujson for ESP32 communication
"""
import ujson
import time


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
    """Handles JSON message protocol for PC communication"""
    
    def __init__(self):
        self.message_delimiter = "\n"
    
    def create_command_message(self, action: str) -> str:
        """Create a command message"""
        message = {
            "type": MessageType.COMMAND,
            "action": action,
            "timestamp": time.time()
        }
        return self._serialize_message(message)
    
    def create_heartbeat_message(self) -> str:
        """Create a heartbeat message"""
        message = {
            "type": MessageType.HEARTBEAT,
            "timestamp": time.time()
        }
        return self._serialize_message(message)
    
    def parse_message(self, raw_message: str):
        """
        Parse a JSON message from PC
        Returns None if not a valid JSON message
        """
        try:
            # Clean the message
            message = raw_message.strip()
            
            # Check if it looks like JSON
            if not (message.startswith('{') and message.endswith('}')):
                return None
            
            # Parse JSON
            parsed = ujson.loads(message)
            
            # Validate basic structure
            if not isinstance(parsed, dict):
                return None
            
            # Validate required fields
            if "type" not in parsed:
                return None
            
            return parsed
            
        except (ValueError, TypeError):
            # Not a valid JSON message, probably debug output
            return None
    
    def validate_system_data_message(self, message: dict) -> bool:
        """Validate a system data message structure"""
        if message.get("type") != MessageType.SYSTEM_DATA:
            return False
        
        required_fields = ["timestamp", "data"]
        return all(field in message for field in required_fields)
    
    def validate_status_message(self, message: dict) -> bool:
        """Validate a status message structure"""
        if message.get("type") != MessageType.STATUS:
            return False
        
        required_fields = ["state", "timestamp"]
        return all(field in message for field in required_fields)
    
    def validate_ack_message(self, message: dict) -> bool:
        """Validate an acknowledgment message structure"""
        if message.get("type") != MessageType.ACK:
            return False
        
        required_fields = ["command", "result", "timestamp"]
        return all(field in message for field in required_fields)
    
    def _serialize_message(self, message: dict) -> str:
        """Serialize message to JSON string"""
        try:
            json_str = ujson.dumps(message)
            return json_str + self.message_delimiter
        except (TypeError, ValueError) as e:
            print(f"Failed to serialize message: {e}")
            return ""
    
    def extract_system_data(self, message: dict):
        """Extract system data from system data message"""
        if not self.validate_system_data_message(message):
            return None
        
        return message.get("data")
    
    def extract_ack_info(self, message: dict):
        """Extract acknowledgment info from ack message"""
        if not self.validate_ack_message(message):
            return None, None, None
        
        return (
            message.get("command"),
            message.get("result"),
            message.get("details")
        )
    
    def is_json_line(self, line: str) -> bool:
        """Quick check if a line might be JSON"""
        stripped = line.strip()
        return stripped.startswith('{') and stripped.endswith('}')


# Global protocol instance
protocol = JSONProtocol()


def create_command_message(action: str) -> str:
    """Convenience function to create command message"""
    return protocol.create_command_message(action)


def create_heartbeat_message() -> str:
    """Convenience function to create heartbeat message"""
    return protocol.create_heartbeat_message()


def parse_message(raw_message: str):
    """Convenience function to parse message"""
    return protocol.parse_message(raw_message)


def is_json_line(line: str) -> bool:
    """Convenience function to check if line is JSON"""
    return protocol.is_json_line(line)


def extract_system_data(message: dict):
    """
    Extract system data from message, handling both old and new formats
    Old format: {"type":"system_data","timestamp":123,"data":{"date":"...","cpu_percent":...}}
    New format: {"type":"system_data","date":"...","cpu":...}
    """
    if not message or message.get("type") != "system_data":
        return None
    
    # Check if this is the old format with nested data
    if "data" in message:
        data = message["data"]
    else:
        # New optimized format - data is directly in message
        data = message
    
    # Extract and normalize field names
    try:
        extracted = {
            "date": data.get("date", "No Data"),
            "time": data.get("time", "No Data"),
            "cpu_percent": data.get("cpu", data.get("cpu_percent", 0.0)),
            "ram_used_gb": data.get("ram_used", data.get("ram_used_gb", 0.0)),
            "ram_total_gb": data.get("ram_total", data.get("ram_total_gb", 0.0)),
            "network_sent_mb": data.get("net_up", data.get("network_sent_mb", 0.0)),
            "network_recv_mb": data.get("net_down", data.get("network_recv_mb", 0.0))
        }
        return extracted
    except Exception as e:
        print(f"Error extracting system data: {e}")
        return None


def extract_ack_info(message: dict):
    """Convenience function to extract ack info"""
    return protocol.extract_ack_info(message)
