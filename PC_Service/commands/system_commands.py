"""
System Commands for ESP32 CYD PC Service
Handles system-level operations like shutdown, restart, sleep
"""
import platform
import time
from .command_executor import (
    ProcessCommandExecutor, ConfirmationCommandExecutor, CommandResult
)
from config import REQUIRE_SHUTDOWN_CONFIRMATION, SHUTDOWN_CONFIRMATION_TIMEOUT


class SystemCommands:
    """Handles system-level commands"""
    
    def __init__(self):
        self.system = platform.system().lower()
        self._setup_executors()
    
    def _setup_executors(self):
        """Setup system command executors based on the operating system"""
        if self.system == "windows":
            # Windows shutdown commands
            shutdown_executor = ProcessCommandExecutor(
                "Shutdown",
                "shutdown /s /t 5 /c \"Shutdown initiated by ESP32 CYD\""
            )
            restart_executor = ProcessCommandExecutor(
                "Restart",
                "shutdown /r /t 5 /c \"Restart initiated by ESP32 CYD\""
            )
            sleep_executor = ProcessCommandExecutor(
                "Sleep",
                "rundll32.exe powrprof.dll,SetSuspendState 0,1,0"
            )
            hibernate_executor = ProcessCommandExecutor(
                "Hibernate",
                "shutdown /h"
            )
            
        elif self.system == "darwin":  # macOS
            shutdown_executor = ProcessCommandExecutor(
                "Shutdown",
                "sudo shutdown -h +1"
            )
            restart_executor = ProcessCommandExecutor(
                "Restart",
                "sudo shutdown -r +1"
            )
            sleep_executor = ProcessCommandExecutor(
                "Sleep",
                "pmset sleepnow"
            )
            hibernate_executor = ProcessCommandExecutor(
                "Hibernate",
                "pmset sleepnow"  # macOS doesn't distinguish hibernate from sleep
            )
            
        elif self.system == "linux":
            shutdown_executor = ProcessCommandExecutor(
                "Shutdown",
                "sudo shutdown -h +1"
            )
            restart_executor = ProcessCommandExecutor(
                "Restart",
                "sudo shutdown -r +1"
            )
            sleep_executor = ProcessCommandExecutor(
                "Sleep",
                "systemctl suspend"
            )
            hibernate_executor = ProcessCommandExecutor(
                "Hibernate",
                "systemctl hibernate"
            )
        else:
            # Unsupported system
            shutdown_executor = None
            restart_executor = None
            sleep_executor = None
            hibernate_executor = None
        
        # Wrap critical commands with confirmation if required
        if REQUIRE_SHUTDOWN_CONFIRMATION:
            self.shutdown_executor = ConfirmationCommandExecutor(
                "Shutdown with Confirmation",
                shutdown_executor,
                SHUTDOWN_CONFIRMATION_TIMEOUT
            ) if shutdown_executor else None
            
            self.restart_executor = ConfirmationCommandExecutor(
                "Restart with Confirmation",
                restart_executor,
                SHUTDOWN_CONFIRMATION_TIMEOUT
            ) if restart_executor else None
        else:
            self.shutdown_executor = shutdown_executor
            self.restart_executor = restart_executor
        
        # Sleep and hibernate don't need confirmation
        self.sleep_executor = sleep_executor
        self.hibernate_executor = hibernate_executor
    
    def shutdown(self) -> CommandResult:
        """Shutdown the system"""
        if not self.shutdown_executor:
            return CommandResult(False, "Shutdown not supported",
                               f"Shutdown not available on {self.system}")
        
        try:
            print("Initiating system shutdown...")
            return self.shutdown_executor.safe_execute()
        except Exception as e:
            return CommandResult(False, "Shutdown failed", str(e))
    
    def restart(self) -> CommandResult:
        """Restart the system"""
        if not self.restart_executor:
            return CommandResult(False, "Restart not supported",
                               f"Restart not available on {self.system}")
        
        try:
            print("Initiating system restart...")
            return self.restart_executor.safe_execute()
        except Exception as e:
            return CommandResult(False, "Restart failed", str(e))
    
    def sleep(self) -> CommandResult:
        """Put the system to sleep"""
        if not self.sleep_executor:
            return CommandResult(False, "Sleep not supported",
                               f"Sleep not available on {self.system}")
        
        try:
            print("Putting system to sleep...")
            return self.sleep_executor.safe_execute()
        except Exception as e:
            return CommandResult(False, "Sleep failed", str(e))
    
    def hibernate(self) -> CommandResult:
        """Hibernate the system"""
        if not self.hibernate_executor:
            return CommandResult(False, "Hibernate not supported",
                               f"Hibernate not available on {self.system}")
        
        try:
            print("Hibernating system...")
            return self.hibernate_executor.safe_execute()
        except Exception as e:
            return CommandResult(False, "Hibernate failed", str(e))
    
    def cancel_shutdown(self) -> CommandResult:
        """Cancel a pending shutdown"""
        try:
            if self.system == "windows":
                cancel_executor = ProcessCommandExecutor(
                    "Cancel Shutdown",
                    "shutdown /a"
                )
            elif self.system in ["darwin", "linux"]:
                # For Unix-like systems, we'd need to kill the shutdown process
                cancel_executor = ProcessCommandExecutor(
                    "Cancel Shutdown",
                    "sudo pkill -f shutdown"
                )
            else:
                return CommandResult(False, "Cancel shutdown not supported",
                                   f"Cancel shutdown not available on {self.system}")
            
            return cancel_executor.safe_execute()
            
        except Exception as e:
            return CommandResult(False, "Failed to cancel shutdown", str(e))
    
    def confirm_shutdown(self, confirmation_id: str) -> CommandResult:
        """Confirm a pending shutdown operation"""
        if (REQUIRE_SHUTDOWN_CONFIRMATION and 
            hasattr(self.shutdown_executor, 'confirm_execution')):
            return self.shutdown_executor.confirm_execution(confirmation_id)
        else:
            return CommandResult(False, "No confirmation required",
                               "Shutdown confirmation is not enabled")
    
    def confirm_restart(self, confirmation_id: str) -> CommandResult:
        """Confirm a pending restart operation"""
        if (REQUIRE_SHUTDOWN_CONFIRMATION and 
            hasattr(self.restart_executor, 'confirm_execution')):
            return self.restart_executor.confirm_execution(confirmation_id)
        else:
            return CommandResult(False, "No confirmation required",
                               "Restart confirmation is not enabled")
    
    def get_system_info(self) -> dict:
        """Get system information"""
        return {
            "system": self.system,
            "platform": platform.platform(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "shutdown_confirmation_required": REQUIRE_SHUTDOWN_CONFIRMATION,
            "shutdown_confirmation_timeout": SHUTDOWN_CONFIRMATION_TIMEOUT,
            "available_commands": self.get_available_commands()
        }
    
    def get_available_commands(self) -> list:
        """Get list of available system commands"""
        commands = []
        
        if self.shutdown_executor:
            commands.append("shutdown")
        if self.restart_executor:
            commands.append("restart")
        if self.sleep_executor:
            commands.append("sleep")
        if self.hibernate_executor:
            commands.append("hibernate")
        
        commands.append("cancel_shutdown")
        
        return commands
    
    def cleanup_expired_confirmations(self):
        """Clean up expired confirmation requests"""
        if (REQUIRE_SHUTDOWN_CONFIRMATION and 
            hasattr(self.shutdown_executor, 'cleanup_expired_confirmations')):
            self.shutdown_executor.cleanup_expired_confirmations()
        
        if (REQUIRE_SHUTDOWN_CONFIRMATION and 
            hasattr(self.restart_executor, 'cleanup_expired_confirmations')):
            self.restart_executor.cleanup_expired_confirmations()


# Global instance
system_commands = SystemCommands()


def shutdown() -> CommandResult:
    """Convenience function to shutdown system"""
    return system_commands.shutdown()


def restart() -> CommandResult:
    """Convenience function to restart system"""
    return system_commands.restart()


def sleep() -> CommandResult:
    """Convenience function to sleep system"""
    return system_commands.sleep()


def hibernate() -> CommandResult:
    """Convenience function to hibernate system"""
    return system_commands.hibernate()


def cancel_shutdown() -> CommandResult:
    """Convenience function to cancel shutdown"""
    return system_commands.cancel_shutdown()


def confirm_shutdown(confirmation_id: str) -> CommandResult:
    """Convenience function to confirm shutdown"""
    return system_commands.confirm_shutdown(confirmation_id)


def confirm_restart(confirmation_id: str) -> CommandResult:
    """Convenience function to confirm restart"""
    return system_commands.confirm_restart(confirmation_id)
