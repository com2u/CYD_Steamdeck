"""
Terminal Commands for ESP32 CYD PC Service
Handles terminal and command prompt operations
"""
import os
import platform
from .command_executor import AsyncProcessCommandExecutor, CommandResult


class TerminalCommands:
    """Handles terminal-related commands"""
    
    def __init__(self):
        self.system = platform.system().lower()
        self._setup_executors()
    
    def _setup_executors(self):
        """Setup command executors based on the operating system"""
        if self.system == "windows":
            # Windows Terminal (preferred) or Command Prompt
            self.terminal_executor = AsyncProcessCommandExecutor(
                "Windows Terminal", 
                "wt.exe"
            )
            self.cmd_executor = AsyncProcessCommandExecutor(
                "Command Prompt",
                "cmd.exe"
            )
            self.powershell_executor = AsyncProcessCommandExecutor(
                "PowerShell",
                "powershell.exe"
            )
        elif self.system == "darwin":  # macOS
            self.terminal_executor = AsyncProcessCommandExecutor(
                "Terminal",
                "open -a Terminal"
            )
        elif self.system == "linux":
            # Try common Linux terminals
            self.terminal_executor = AsyncProcessCommandExecutor(
                "Terminal",
                "gnome-terminal || xterm || konsole || x-terminal-emulator"
            )
        else:
            # Fallback
            self.terminal_executor = AsyncProcessCommandExecutor(
                "Terminal",
                "xterm"
            )
    
    def open_terminal(self) -> CommandResult:
        """Open the default terminal"""
        try:
            if self.system == "windows":
                # Try Windows Terminal first, fallback to cmd
                result = self.terminal_executor.safe_execute()
                if not result.success:
                    print("Windows Terminal not available, trying Command Prompt...")
                    result = self.cmd_executor.safe_execute()
                return result
            else:
                return self.terminal_executor.safe_execute()
                
        except Exception as e:
            return CommandResult(False, "Failed to open terminal", str(e))
    
    def open_command_prompt(self) -> CommandResult:
        """Open Command Prompt (Windows specific)"""
        if self.system != "windows":
            return CommandResult(False, "Command Prompt not available", 
                               "Command Prompt is Windows-specific")
        
        return self.cmd_executor.safe_execute()
    
    def open_powershell(self) -> CommandResult:
        """Open PowerShell (Windows specific)"""
        if self.system != "windows":
            return CommandResult(False, "PowerShell not available",
                               "PowerShell is Windows-specific")
        
        return self.powershell_executor.safe_execute()
    
    def open_terminal_with_command(self, command: str) -> CommandResult:
        """Open terminal and execute a specific command"""
        try:
            if self.system == "windows":
                # Windows Terminal with command
                full_command = f'wt.exe cmd /k "{command}"'
                executor = AsyncProcessCommandExecutor(
                    "Terminal with Command",
                    full_command
                )
            elif self.system == "darwin":  # macOS
                # Terminal with command
                full_command = f'osascript -e \'tell app "Terminal" to do script "{command}"\''
                executor = AsyncProcessCommandExecutor(
                    "Terminal with Command",
                    full_command
                )
            elif self.system == "linux":
                # Linux terminal with command
                full_command = f'gnome-terminal -- bash -c "{command}; exec bash"'
                executor = AsyncProcessCommandExecutor(
                    "Terminal with Command",
                    full_command
                )
            else:
                return CommandResult(False, "Unsupported system",
                                   f"Terminal with command not supported on {self.system}")
            
            return executor.safe_execute()
            
        except Exception as e:
            return CommandResult(False, "Failed to open terminal with command", str(e))
    
    def get_available_terminals(self) -> list:
        """Get list of available terminal applications"""
        terminals = []
        
        if self.system == "windows":
            terminals = [
                {"name": "Windows Terminal", "command": "wt.exe"},
                {"name": "Command Prompt", "command": "cmd.exe"},
                {"name": "PowerShell", "command": "powershell.exe"}
            ]
        elif self.system == "darwin":
            terminals = [
                {"name": "Terminal", "command": "open -a Terminal"},
                {"name": "iTerm2", "command": "open -a iTerm"}
            ]
        elif self.system == "linux":
            terminals = [
                {"name": "GNOME Terminal", "command": "gnome-terminal"},
                {"name": "XTerm", "command": "xterm"},
                {"name": "Konsole", "command": "konsole"},
                {"name": "XFCE Terminal", "command": "xfce4-terminal"}
            ]
        
        return terminals


# Global instance
terminal_commands = TerminalCommands()


def open_terminal() -> CommandResult:
    """Convenience function to open terminal"""
    return terminal_commands.open_terminal()


def open_command_prompt() -> CommandResult:
    """Convenience function to open command prompt"""
    return terminal_commands.open_command_prompt()


def open_powershell() -> CommandResult:
    """Convenience function to open PowerShell"""
    return terminal_commands.open_powershell()


def open_terminal_with_command(command: str) -> CommandResult:
    """Convenience function to open terminal with command"""
    return terminal_commands.open_terminal_with_command(command)
