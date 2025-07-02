"""
ESP32 CYD PC Service - Main Entry Point
Handles ESP32 display communication and PC command execution
"""
import sys
import signal
import argparse
import time
from core.service_manager import create_service_manager
from config import DEFAULT_SERIAL_PORT, SERVICE_NAME, VERSION


def signal_handler(signum, frame):
    """Handle Ctrl+C gracefully"""
    print("\nShutdown signal received...")
    global service_manager
    if service_manager:
        service_manager.stop()
    sys.exit(0)


def print_banner():
    """Print service banner"""
    print("=" * 60)
    print(f"  {SERVICE_NAME} v{VERSION}")
    print("  ESP32 Display to PC Communication Service")
    print("=" * 60)
    print()


def print_help():
    """Print usage help"""
    print("Available commands while running:")
    print("  status  - Show service status")
    print("  test    - Send test message to ESP32")
    print("  update  - Force system update")
    print("  port    - Change serial port")
    print("  help    - Show this help")
    print("  quit    - Stop the service")
    print()


def interactive_mode(service_manager):
    """Run interactive command mode"""
    print("Interactive mode enabled. Type 'help' for commands.")
    print("Press Ctrl+C to exit.")
    print()
    
    while service_manager.running:
        try:
            command = input("CYD> ").strip().lower()
            
            if command == "quit" or command == "exit":
                break
            elif command == "status":
                status = service_manager.get_status()
                print("\n=== Service Status ===")
                print(f"Running: {status['running']}")
                print(f"Port: {status['port']}")
                print(f"Uptime: {status['uptime_seconds']:.1f} seconds")
                print(f"Commands processed: {status['commands_processed']}")
                if 'serial' in status:
                    serial_status = status['serial']
                    print(f"Serial connected: {serial_status['connected']}")
                    print(f"Messages sent: {serial_status['messages_sent']}")
                    print(f"Messages received: {serial_status['messages_received']}")
                print()
                
            elif command == "test":
                service_manager.send_test_message()
                
            elif command == "update":
                service_manager.force_system_update()
                
            elif command == "port":
                new_port = input("Enter new port (e.g., COM7): ").strip()
                if new_port:
                    if service_manager.change_port(new_port):
                        print(f"Port changed to {new_port}")
                    else:
                        print("Failed to change port")
                        
            elif command == "help":
                print_help()
                
            elif command == "":
                continue
                
            else:
                print(f"Unknown command: {command}")
                print("Type 'help' for available commands.")
                
        except KeyboardInterrupt:
            break
        except EOFError:
            break
        except Exception as e:
            print(f"Error: {e}")


def main():
    """Main entry point"""
    global service_manager
    service_manager = None
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description=f"{SERVICE_NAME} v{VERSION}",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                    # Use default port (COM7)
  python main.py --port COM8        # Use specific port
  python main.py --no-interactive   # Run without interactive mode
        """
    )
    
    parser.add_argument(
        "--port", "-p",
        default=DEFAULT_SERIAL_PORT,
        help=f"Serial port to use (default: {DEFAULT_SERIAL_PORT})"
    )
    
    parser.add_argument(
        "--no-interactive", "-n",
        action="store_true",
        help="Disable interactive command mode"
    )
    
    parser.add_argument(
        "--version", "-v",
        action="version",
        version=f"{SERVICE_NAME} v{VERSION}"
    )
    
    args = parser.parse_args()
    
    # Print banner
    print_banner()
    
    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Create and start service manager
        service_manager = create_service_manager(args.port)
        
        if not service_manager.start():
            print("Failed to start service")
            return 1
        
        # Run interactive mode or just wait
        if not args.no_interactive:
            interactive_mode(service_manager)
        else:
            print("Service running in background mode...")
            print("Press Ctrl+C to stop")
            try:
                while service_manager.running:
                    time.sleep(1)
            except KeyboardInterrupt:
                pass
        
    except Exception as e:
        print(f"Fatal error: {e}")
        return 1
    
    finally:
        # Cleanup
        if service_manager:
            service_manager.stop()
    
    print("Service shutdown complete")
    return 0


if __name__ == "__main__":
    sys.exit(main())
