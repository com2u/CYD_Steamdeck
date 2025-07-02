"""
Browser Commands for ESP32 CYD PC Service
Handles browser operations and web application launching
"""
import os
import platform
import webbrowser
from .command_executor import AsyncProcessCommandExecutor, CommandResult


class BrowserCommands:
    """Handles browser-related commands"""
    
    def __init__(self):
        self.system = platform.system().lower()
        self._setup_executors()
    
    def _setup_executors(self):
        """Setup browser executors based on the operating system"""
        if self.system == "windows":
            self.chrome_executor = AsyncProcessCommandExecutor(
                "Chrome",
                "start chrome"
            )
            self.edge_executor = AsyncProcessCommandExecutor(
                "Edge",
                "start msedge"
            )
            self.firefox_executor = AsyncProcessCommandExecutor(
                "Firefox",
                "start firefox"
            )
        elif self.system == "darwin":  # macOS
            self.chrome_executor = AsyncProcessCommandExecutor(
                "Chrome",
                "open -a 'Google Chrome'"
            )
            self.safari_executor = AsyncProcessCommandExecutor(
                "Safari",
                "open -a Safari"
            )
            self.firefox_executor = AsyncProcessCommandExecutor(
                "Firefox",
                "open -a Firefox"
            )
        elif self.system == "linux":
            self.chrome_executor = AsyncProcessCommandExecutor(
                "Chrome",
                "google-chrome || chromium-browser || chromium"
            )
            self.firefox_executor = AsyncProcessCommandExecutor(
                "Firefox",
                "firefox"
            )
        else:
            # Fallback using webbrowser module
            self.default_executor = None
    
    def open_browser(self, browser_name: str = "default") -> CommandResult:
        """Open specified browser or default browser"""
        try:
            if browser_name.lower() == "default":
                return self._open_default_browser()
            elif browser_name.lower() == "chrome":
                return self._open_chrome()
            elif browser_name.lower() == "firefox":
                return self._open_firefox()
            elif browser_name.lower() == "edge":
                return self._open_edge()
            elif browser_name.lower() == "safari":
                return self._open_safari()
            else:
                return CommandResult(False, f"Unknown browser: {browser_name}",
                                   "Supported browsers: default, chrome, firefox, edge, safari")
                
        except Exception as e:
            return CommandResult(False, "Failed to open browser", str(e))
    
    def open_url(self, url: str, browser_name: str = "default") -> CommandResult:
        """Open a specific URL in the specified browser"""
        try:
            # Validate URL format
            if not url.startswith(('http://', 'https://', 'file://')):
                if not url.startswith('www.'):
                    url = 'https://www.' + url
                else:
                    url = 'https://' + url
            
            if browser_name.lower() == "default":
                # Use Python's webbrowser module for default browser
                webbrowser.open(url)
                return CommandResult(True, f"Opened {url} in default browser")
            else:
                # Open specific browser with URL
                if self.system == "windows":
                    if browser_name.lower() == "chrome":
                        command = f'start chrome "{url}"'
                    elif browser_name.lower() == "edge":
                        command = f'start msedge "{url}"'
                    elif browser_name.lower() == "firefox":
                        command = f'start firefox "{url}"'
                    else:
                        return CommandResult(False, f"Unsupported browser: {browser_name}")
                elif self.system == "darwin":
                    if browser_name.lower() == "chrome":
                        command = f'open -a "Google Chrome" "{url}"'
                    elif browser_name.lower() == "safari":
                        command = f'open -a Safari "{url}"'
                    elif browser_name.lower() == "firefox":
                        command = f'open -a Firefox "{url}"'
                    else:
                        return CommandResult(False, f"Unsupported browser: {browser_name}")
                elif self.system == "linux":
                    if browser_name.lower() == "chrome":
                        command = f'google-chrome "{url}" || chromium-browser "{url}" || chromium "{url}"'
                    elif browser_name.lower() == "firefox":
                        command = f'firefox "{url}"'
                    else:
                        return CommandResult(False, f"Unsupported browser: {browser_name}")
                else:
                    # Fallback to default browser
                    webbrowser.open(url)
                    return CommandResult(True, f"Opened {url} in default browser")
                
                executor = AsyncProcessCommandExecutor(f"{browser_name} with URL", command)
                return executor.safe_execute()
                
        except Exception as e:
            return CommandResult(False, "Failed to open URL", str(e))
    
    def _open_default_browser(self) -> CommandResult:
        """Open the default system browser"""
        try:
            # Use Python's webbrowser module
            webbrowser.open('about:blank')
            return CommandResult(True, "Default browser opened")
        except Exception as e:
            return CommandResult(False, "Failed to open default browser", str(e))
    
    def _open_chrome(self) -> CommandResult:
        """Open Google Chrome"""
        if hasattr(self, 'chrome_executor'):
            return self.chrome_executor.safe_execute()
        else:
            return CommandResult(False, "Chrome not available", 
                               f"Chrome not configured for {self.system}")
    
    def _open_firefox(self) -> CommandResult:
        """Open Firefox"""
        if hasattr(self, 'firefox_executor'):
            return self.firefox_executor.safe_execute()
        else:
            return CommandResult(False, "Firefox not available",
                               f"Firefox not configured for {self.system}")
    
    def _open_edge(self) -> CommandResult:
        """Open Microsoft Edge"""
        if hasattr(self, 'edge_executor'):
            return self.edge_executor.safe_execute()
        else:
            return CommandResult(False, "Edge not available",
                               "Edge is only available on Windows")
    
    def _open_safari(self) -> CommandResult:
        """Open Safari"""
        if hasattr(self, 'safari_executor'):
            return self.safari_executor.safe_execute()
        else:
            return CommandResult(False, "Safari not available",
                               "Safari is only available on macOS")
    
    def open_test_page(self) -> CommandResult:
        """Open a test page to verify browser functionality"""
        test_urls = [
            "https://www.google.com",
            "https://www.example.com",
            "https://httpbin.org/get"
        ]
        
        # Try to open Google as test page
        return self.open_url(test_urls[0])
    
    def get_available_browsers(self) -> list:
        """Get list of available browsers for the current system"""
        browsers = []
        
        if self.system == "windows":
            browsers = [
                {"name": "Chrome", "command": "chrome"},
                {"name": "Edge", "command": "edge"},
                {"name": "Firefox", "command": "firefox"},
                {"name": "Default", "command": "default"}
            ]
        elif self.system == "darwin":
            browsers = [
                {"name": "Chrome", "command": "chrome"},
                {"name": "Safari", "command": "safari"},
                {"name": "Firefox", "command": "firefox"},
                {"name": "Default", "command": "default"}
            ]
        elif self.system == "linux":
            browsers = [
                {"name": "Chrome", "command": "chrome"},
                {"name": "Firefox", "command": "firefox"},
                {"name": "Default", "command": "default"}
            ]
        else:
            browsers = [
                {"name": "Default", "command": "default"}
            ]
        
        return browsers


# Global instance
browser_commands = BrowserCommands()


def open_browser(browser_name: str = "default") -> CommandResult:
    """Convenience function to open browser"""
    return browser_commands.open_browser(browser_name)


def open_chrome() -> CommandResult:
    """Convenience function to open Chrome"""
    return browser_commands.open_browser("chrome")


def open_test_page() -> CommandResult:
    """Convenience function to open test page"""
    return browser_commands.open_test_page()


def open_url(url: str, browser_name: str = "default") -> CommandResult:
    """Convenience function to open URL"""
    return browser_commands.open_url(url, browser_name)
