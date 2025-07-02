"""
System Monitor for ESP32 CYD PC Service
Collects system information (CPU, RAM, Network) for display on ESP32
"""
import psutil
import time
from datetime import datetime
from typing import Dict, Any
from config import CPU_SAMPLE_INTERVAL


class SystemMonitor:
    """Monitors system resources and provides formatted data"""
    
    def __init__(self):
        self.last_network_stats = None
        self.last_network_time = None
        self._initialize_network_baseline()
    
    def _initialize_network_baseline(self):
        """Initialize network statistics baseline"""
        try:
            self.last_network_stats = psutil.net_io_counters()
            self.last_network_time = time.time()
        except Exception:
            self.last_network_stats = None
            self.last_network_time = None
    
    def get_system_data(self) -> Dict[str, Any]:
        """
        Collect all system information
        Returns formatted data ready for ESP32 display
        """
        current_time = datetime.now()
        
        data = {
            "date": current_time.strftime("%Y-%m-%d"),
            "time": current_time.strftime("%H:%M:%S"),
            "cpu_percent": self.get_cpu_usage(),
            "ram_used_gb": self.get_ram_usage()["used_gb"],
            "ram_total_gb": self.get_ram_usage()["total_gb"],
            "network_sent_mb": self.get_network_usage()["sent_mb"],
            "network_recv_mb": self.get_network_usage()["recv_mb"]
        }
        
        return data
    
    def get_cpu_usage(self) -> float:
        """Get CPU usage percentage"""
        try:
            # Get CPU percentage with a short interval for accuracy
            cpu_percent = psutil.cpu_percent(interval=CPU_SAMPLE_INTERVAL)
            return round(cpu_percent, 1)
        except Exception as e:
            print(f"Error getting CPU usage: {e}")
            return 0.0
    
    def get_ram_usage(self) -> Dict[str, float]:
        """Get RAM usage information"""
        try:
            memory = psutil.virtual_memory()
            
            # Convert bytes to GB
            total_gb = round(memory.total / (1024**3), 1)
            used_gb = round(memory.used / (1024**3), 1)
            available_gb = round(memory.available / (1024**3), 1)
            percent = round(memory.percent, 1)
            
            return {
                "total_gb": total_gb,
                "used_gb": used_gb,
                "available_gb": available_gb,
                "percent": percent
            }
        except Exception as e:
            print(f"Error getting RAM usage: {e}")
            return {
                "total_gb": 0.0,
                "used_gb": 0.0,
                "available_gb": 0.0,
                "percent": 0.0
            }
    
    def get_network_usage(self) -> Dict[str, float]:
        """Get network usage information (cumulative since boot)"""
        try:
            current_stats = psutil.net_io_counters()
            current_time = time.time()
            
            if current_stats:
                # Convert bytes to MB
                sent_mb = round(current_stats.bytes_sent / (1024**2), 1)
                recv_mb = round(current_stats.bytes_recv / (1024**2), 1)
                
                # Calculate rates if we have previous data
                sent_rate_mbps = 0.0
                recv_rate_mbps = 0.0
                
                if self.last_network_stats and self.last_network_time:
                    time_diff = current_time - self.last_network_time
                    if time_diff > 0:
                        sent_diff = current_stats.bytes_sent - self.last_network_stats.bytes_sent
                        recv_diff = current_stats.bytes_recv - self.last_network_stats.bytes_recv
                        
                        # Convert to Mbps
                        sent_rate_mbps = round((sent_diff * 8) / (time_diff * 1024**2), 2)
                        recv_rate_mbps = round((recv_diff * 8) / (time_diff * 1024**2), 2)
                
                # Update baseline for next calculation
                self.last_network_stats = current_stats
                self.last_network_time = current_time
                
                return {
                    "sent_mb": sent_mb,
                    "recv_mb": recv_mb,
                    "sent_rate_mbps": sent_rate_mbps,
                    "recv_rate_mbps": recv_rate_mbps
                }
            else:
                return {
                    "sent_mb": 0.0,
                    "recv_mb": 0.0,
                    "sent_rate_mbps": 0.0,
                    "recv_rate_mbps": 0.0
                }
                
        except Exception as e:
            print(f"Error getting network usage: {e}")
            return {
                "sent_mb": 0.0,
                "recv_mb": 0.0,
                "sent_rate_mbps": 0.0,
                "recv_rate_mbps": 0.0
            }
    
    def get_disk_usage(self, path: str = "C:\\") -> Dict[str, float]:
        """Get disk usage information for specified path"""
        try:
            disk = psutil.disk_usage(path)
            
            # Convert bytes to GB
            total_gb = round(disk.total / (1024**3), 1)
            used_gb = round(disk.used / (1024**3), 1)
            free_gb = round(disk.free / (1024**3), 1)
            percent = round((disk.used / disk.total) * 100, 1)
            
            return {
                "total_gb": total_gb,
                "used_gb": used_gb,
                "free_gb": free_gb,
                "percent": percent,
                "path": path
            }
        except Exception as e:
            print(f"Error getting disk usage for {path}: {e}")
            return {
                "total_gb": 0.0,
                "used_gb": 0.0,
                "free_gb": 0.0,
                "percent": 0.0,
                "path": path
            }
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get general system information"""
        try:
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            uptime = datetime.now() - boot_time
            
            return {
                "hostname": psutil.os.uname().nodename if hasattr(psutil.os, 'uname') else "Unknown",
                "platform": psutil.os.name,
                "boot_time": boot_time.strftime("%Y-%m-%d %H:%M:%S"),
                "uptime_days": uptime.days,
                "uptime_hours": uptime.seconds // 3600,
                "uptime_minutes": (uptime.seconds % 3600) // 60
            }
        except Exception as e:
            print(f"Error getting system info: {e}")
            return {
                "hostname": "Unknown",
                "platform": "Unknown",
                "boot_time": "Unknown",
                "uptime_days": 0,
                "uptime_hours": 0,
                "uptime_minutes": 0
            }
    
    def get_formatted_summary(self) -> str:
        """Get a formatted summary string for logging"""
        data = self.get_system_data()
        return (f"CPU: {data['cpu_percent']}% | "
                f"RAM: {data['ram_used_gb']}/{data['ram_total_gb']}GB | "
                f"NET: ↑{data['network_sent_mb']}MB ↓{data['network_recv_mb']}MB")


# Global monitor instance
monitor = SystemMonitor()


def get_system_data() -> Dict[str, Any]:
    """Convenience function to get system data"""
    return monitor.get_system_data()


def get_formatted_summary() -> str:
    """Convenience function to get formatted summary"""
    return monitor.get_formatted_summary()
