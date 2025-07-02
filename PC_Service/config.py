"""
Configuration settings for ESP32 CYD PC Service
"""
import os

# Serial Communication Settings
DEFAULT_SERIAL_PORT = "COM7"
BAUD_RATE = 115200
SERIAL_TIMEOUT = 1.0
RECONNECT_DELAY = 2.0
MAX_RECONNECT_ATTEMPTS = 0  # 0 = infinite attempts

# System Monitoring Settings
SYSTEM_UPDATE_INTERVAL = 10  # seconds
CPU_SAMPLE_INTERVAL = 1.0   # seconds for CPU percentage calculation

# JSON Protocol Settings
MESSAGE_DELIMITER = "\n"
MAX_MESSAGE_LENGTH = 1024
JSON_INDENT = None  # None for compact JSON, 2 for pretty printing

# Logging Settings
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_TO_FILE = True
LOG_FILE = "pc_service.log"
MAX_LOG_SIZE = 10 * 1024 * 1024  # 10MB
LOG_BACKUP_COUNT = 5

# Command Execution Settings
COMMAND_TIMEOUT = 30.0  # seconds
REQUIRE_SHUTDOWN_CONFIRMATION = True
SHUTDOWN_CONFIRMATION_TIMEOUT = 10.0  # seconds

# Application Settings
SERVICE_NAME = "ESP32 CYD PC Service"
VERSION = "1.0.0"
DEBUG_MODE = False

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(BASE_DIR, "logs")

# Create log directory if it doesn't exist
os.makedirs(LOG_DIR, exist_ok=True)
