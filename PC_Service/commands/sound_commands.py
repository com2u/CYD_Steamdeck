"""
Sound Commands for ESP32 CYD PC Service
Handles playing sound files in the background
"""
import os
import subprocess
import threading
from .command_executor import CommandResult


def play_sound(sound_name: str) -> CommandResult:
    """
    Play a sound file in the background
    
    Args:
        sound_name: Name of the sound (without .mp3 extension)
        
    Returns:
        CommandResult with success status and message
    """
    try:
        # Get the sound file path
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        sound_file = os.path.join(base_dir, "sound", f"{sound_name.lower()}.mp3")
        
        # Check if sound file exists
        if not os.path.exists(sound_file):
            return CommandResult(False, f"Sound file not found: {sound_file}")
        
        # Play sound in background thread to avoid blocking
        def play_in_background():
            try:
                # Use Windows Media Player for background playback
                subprocess.run([
                    "powershell", "-Command", 
                    f"Add-Type -AssemblyName presentationCore; "
                    f"$mediaPlayer = New-Object system.windows.media.mediaplayer; "
                    f"$mediaPlayer.open([uri]'{sound_file}'); "
                    f"$mediaPlayer.Play(); "
                    f"Start-Sleep -Seconds 1; "
                    f"while($mediaPlayer.NaturalDuration.HasTimeSpan -eq $false) {{ Start-Sleep -Milliseconds 100 }}; "
                    f"$duration = $mediaPlayer.NaturalDuration.TimeSpan.TotalSeconds; "
                    f"Start-Sleep -Seconds $duration; "
                    f"$mediaPlayer.Stop(); "
                    f"$mediaPlayer.Close()"
                ], check=False, capture_output=True)
            except Exception as e:
                print(f"Error playing sound in background: {e}")
        
        # Start background thread
        sound_thread = threading.Thread(target=play_in_background, daemon=True)
        sound_thread.start()
        
        return CommandResult(True, f"Playing sound: {sound_name}")
        
    except Exception as e:
        return CommandResult(False, f"Error playing sound {sound_name}: {str(e)}")


def play_alarm() -> CommandResult:
    """Play alarm sound"""
    return play_sound("alarm")


def play_car() -> CommandResult:
    """Play car sound"""
    return play_sound("car")


def play_bell() -> CommandResult:
    """Play bell sound"""
    return play_sound("bell")


def play_dog() -> CommandResult:
    """Play dog sound"""
    return play_sound("dog")


def play_police() -> CommandResult:
    """Play police sound"""
    return play_sound("police")


def play_tick() -> CommandResult:
    """Play tick sound"""
    return play_sound("tick")


def play_modem() -> CommandResult:
    """Play modem sound"""
    return play_sound("modem")


def play_applause() -> CommandResult:
    """Play applause sound"""
    return play_sound("applause")
