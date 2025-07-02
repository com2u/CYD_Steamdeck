"""
Base Command Executor for ESP32 CYD PC Service
Provides framework for safe command execution with validation
"""
import subprocess
import threading
import time
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Callable
from config import COMMAND_TIMEOUT


class CommandResult:
    """Represents the result of a command execution"""
    
    def __init__(self, success: bool, message: str, details: Optional[str] = None, 
                 return_code: Optional[int] = None):
        self.success = success
        self.message = message
        self.details = details
        self.return_code = return_code
        self.timestamp = time.time()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "success": self.success,
            "message": self.message,
            "details": self.details,
            "return_code": self.return_code,
            "timestamp": self.timestamp
        }


class BaseCommandExecutor(ABC):
    """Base class for command executors"""
    
    def __init__(self, name: str):
        self.name = name
        self.timeout = COMMAND_TIMEOUT
        self.last_execution_time = None
        self.execution_count = 0
    
    @abstractmethod
    def execute(self, **kwargs) -> CommandResult:
        """Execute the command - must be implemented by subclasses"""
        pass
    
    def validate_parameters(self, **kwargs) -> bool:
        """Validate command parameters - can be overridden by subclasses"""
        return True
    
    def pre_execute_hook(self, **kwargs) -> bool:
        """Hook called before execution - can be overridden by subclasses"""
        return True
    
    def post_execute_hook(self, result: CommandResult, **kwargs):
        """Hook called after execution - can be overridden by subclasses"""
        pass
    
    def safe_execute(self, **kwargs) -> CommandResult:
        """Safely execute command with validation and error handling"""
        try:
            # Update statistics
            self.execution_count += 1
            self.last_execution_time = time.time()
            
            # Validate parameters
            if not self.validate_parameters(**kwargs):
                return CommandResult(False, "Invalid parameters", 
                                   f"Parameter validation failed for {self.name}")
            
            # Pre-execution hook
            if not self.pre_execute_hook(**kwargs):
                return CommandResult(False, "Pre-execution check failed",
                                   f"Pre-execution hook failed for {self.name}")
            
            # Execute the command
            result = self.execute(**kwargs)
            
            # Post-execution hook
            self.post_execute_hook(result, **kwargs)
            
            return result
            
        except Exception as e:
            error_msg = f"Unexpected error executing {self.name}: {str(e)}"
            print(error_msg)
            return CommandResult(False, "Execution error", error_msg)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get execution statistics"""
        return {
            "name": self.name,
            "execution_count": self.execution_count,
            "last_execution_time": self.last_execution_time
        }


class ProcessCommandExecutor(BaseCommandExecutor):
    """Command executor that runs system processes"""
    
    def __init__(self, name: str, command: str, shell: bool = True):
        super().__init__(name)
        self.command = command
        self.shell = shell
    
    def execute(self, **kwargs) -> CommandResult:
        """Execute a system process"""
        try:
            print(f"Executing command: {self.command}")
            
            # Start the process
            process = subprocess.Popen(
                self.command,
                shell=self.shell,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait for completion with timeout
            try:
                stdout, stderr = process.communicate(timeout=self.timeout)
                return_code = process.returncode
                
                if return_code == 0:
                    return CommandResult(True, f"{self.name} executed successfully",
                                       stdout.strip() if stdout else None, return_code)
                else:
                    return CommandResult(False, f"{self.name} failed",
                                       stderr.strip() if stderr else f"Return code: {return_code}",
                                       return_code)
                    
            except subprocess.TimeoutExpired:
                process.kill()
                return CommandResult(False, f"{self.name} timed out",
                                   f"Command timed out after {self.timeout} seconds")
                
        except Exception as e:
            return CommandResult(False, f"Failed to execute {self.name}",
                               f"Error: {str(e)}")


class AsyncProcessCommandExecutor(BaseCommandExecutor):
    """Command executor that starts processes asynchronously (fire and forget)"""
    
    def __init__(self, name: str, command: str, shell: bool = True):
        super().__init__(name)
        self.command = command
        self.shell = shell
    
    def execute(self, **kwargs) -> CommandResult:
        """Execute a system process asynchronously"""
        try:
            print(f"Starting async command: {self.command}")
            
            # Start the process without waiting
            process = subprocess.Popen(
                self.command,
                shell=self.shell,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            # Give it a moment to start
            time.sleep(0.5)
            
            # Check if it's still running (successful start)
            if process.poll() is None:
                return CommandResult(True, f"{self.name} started successfully",
                                   f"Process started with PID: {process.pid}")
            else:
                return CommandResult(False, f"{self.name} failed to start",
                                   f"Process exited immediately with code: {process.returncode}")
                
        except Exception as e:
            return CommandResult(False, f"Failed to start {self.name}",
                               f"Error: {str(e)}")


class ConfirmationCommandExecutor(BaseCommandExecutor):
    """Command executor that requires user confirmation"""
    
    def __init__(self, name: str, command_executor: BaseCommandExecutor,
                 confirmation_timeout: float = 10.0):
        super().__init__(name)
        self.command_executor = command_executor
        self.confirmation_timeout = confirmation_timeout
        self.pending_confirmations = {}
    
    def execute(self, **kwargs) -> CommandResult:
        """Execute command with confirmation requirement"""
        confirmation_id = f"{self.name}_{int(time.time())}"
        
        # Store the pending confirmation
        self.pending_confirmations[confirmation_id] = {
            "executor": self.command_executor,
            "kwargs": kwargs,
            "timestamp": time.time()
        }
        
        return CommandResult(False, f"{self.name} requires confirmation",
                           f"Confirmation ID: {confirmation_id}. "
                           f"Confirm within {self.confirmation_timeout} seconds.")
    
    def confirm_execution(self, confirmation_id: str) -> CommandResult:
        """Confirm and execute the pending command"""
        if confirmation_id not in self.pending_confirmations:
            return CommandResult(False, "Invalid confirmation ID",
                               "Confirmation ID not found or expired")
        
        pending = self.pending_confirmations[confirmation_id]
        
        # Check timeout
        if time.time() - pending["timestamp"] > self.confirmation_timeout:
            del self.pending_confirmations[confirmation_id]
            return CommandResult(False, "Confirmation timeout",
                               "Confirmation window has expired")
        
        # Execute the command
        try:
            result = pending["executor"].safe_execute(**pending["kwargs"])
            del self.pending_confirmations[confirmation_id]
            return result
        except Exception as e:
            del self.pending_confirmations[confirmation_id]
            return CommandResult(False, "Execution error after confirmation",
                               f"Error: {str(e)}")
    
    def cleanup_expired_confirmations(self):
        """Remove expired confirmations"""
        current_time = time.time()
        expired_ids = [
            conf_id for conf_id, pending in self.pending_confirmations.items()
            if current_time - pending["timestamp"] > self.confirmation_timeout
        ]
        
        for conf_id in expired_ids:
            del self.pending_confirmations[conf_id]
