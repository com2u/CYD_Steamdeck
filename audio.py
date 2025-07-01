"""
Audio module for ESP32-2432S028R (Cheap Yellow Display)
Handles speaker functionality via PWM on Pin 26
"""
import time
from machine import Pin, PWM

# Audio pin configuration
SPEAKER_PIN = 26

class AudioManager:
    """Manages audio output via PWM speaker"""
    
    def __init__(self):
        self.speaker_pin = Pin(SPEAKER_PIN, Pin.OUT)
        self.pwm = None
        self.is_playing = False
        
    def init_speaker(self):
        """Initialize the PWM speaker"""
        try:
            self.pwm = PWM(self.speaker_pin)
            print("Speaker initialized on Pin", SPEAKER_PIN)
            return True
        except Exception as e:
            print("Failed to initialize speaker:", e)
            return False
    
    def play_tone(self, frequency, duration_ms):
        """
        Play a tone at specified frequency for specified duration
        
        Args:
            frequency (int): Frequency in Hz
            duration_ms (int): Duration in milliseconds
        """
        try:
            self.is_playing = True
            print(f"Playing tone: {frequency}Hz for {duration_ms}ms")
            
            # Reinitialize PWM for each tone to avoid conflicts
            if self.pwm:
                self.pwm.deinit()
            
            self.pwm = PWM(self.speaker_pin)
            
            # Set frequency and duty cycle (50% for clear tone)
            self.pwm.freq(frequency)
            self.pwm.duty(512)  # 50% duty cycle (1024 max)
            
            # Play for specified duration
            time.sleep_ms(duration_ms)
            
            # Stop the tone
            self.stop_tone()
            print("Tone completed")
            
        except Exception as e:
            print("Error playing tone:", e)
            self.stop_tone()
    
    def stop_tone(self):
        """Stop any currently playing tone"""
        if self.pwm:
            try:
                self.pwm.duty(0)  # Set duty to 0 to stop sound
                self.is_playing = False
            except Exception as e:
                print("Error stopping tone:", e)
    
    def play_startup_tone(self):
        """Play startup tone - A3 (220Hz) for 200ms"""
        print("Playing startup tone...")
        self.play_tone(220, 50)  # A3 note (220Hz as requested)
    
    def play_button_click_tone(self):
        """Play button click tone - A4 (440Hz) for 200ms"""
        print("Playing button click tone...")
        self.play_tone(440, 200)  # A4 note (440Hz as requested)
    
    def play_error_tone(self):
        """Play error tone - Low frequency for errors"""
        print("Playing error tone...")
        self.play_tone(220, 500)  # Lower A note for errors
    
    def play_success_tone(self):
        """Play success tone - Two quick high tones"""
        print("Playing success tone...")
        self.play_tone(880, 100)
        time.sleep_ms(50)
        self.play_tone(1108, 100)  # C6 note
    
    def play_melody(self, notes, durations):
        """
        Play a melody with specified notes and durations
        
        Args:
            notes (list): List of frequencies in Hz
            durations (list): List of durations in milliseconds
        """
        if len(notes) != len(durations):
            print("Notes and durations lists must be the same length")
            return
            
        for note, duration in zip(notes, durations):
            if note > 0:  # 0 frequency = rest/pause
                self.play_tone(note, duration)
            else:
                time.sleep_ms(duration)
            time.sleep_ms(50)  # Small gap between notes
    
    def cleanup(self):
        """Clean up PWM resources"""
        if self.pwm:
            try:
                self.stop_tone()
                self.pwm.deinit()
                print("Speaker PWM cleaned up")
            except Exception as e:
                print("Error cleaning up speaker:", e)


# Musical note frequencies (in Hz) for reference
class Notes:
    """Musical note frequencies"""
    # Octave 4
    C4 = 262
    CS4 = 277  # C#
    D4 = 294
    DS4 = 311  # D#
    E4 = 330
    F4 = 349
    FS4 = 370  # F#
    G4 = 392
    GS4 = 415  # G#
    A4 = 440
    AS4 = 466  # A#
    B4 = 494
    
    # Octave 5
    C5 = 523
    CS5 = 554
    D5 = 587
    DS5 = 622
    E5 = 659
    F5 = 698
    FS5 = 740
    G5 = 784
    GS5 = 831
    A5 = 880
    AS5 = 932
    B5 = 988
    
    # Octave 6
    C6 = 1047
    CS6 = 1109
    D6 = 1175
    DS6 = 1245
    E6 = 1319
    F6 = 1397
    FS6 = 1480
    G6 = 1568
    GS6 = 1661
    A6 = 1760
    AS6 = 1865
    B6 = 1976
    
    # Special
    REST = 0  # Silence/pause


# Predefined melodies
class Melodies:
    """Predefined melodies for common events"""
    
    @staticmethod
    def startup():
        """Startup melody"""
        return [Notes.A4], [200]
    
    @staticmethod
    def button_click():
        """Button click sound"""
        return [Notes.A5], [200]
    
    @staticmethod
    def success():
        """Success melody"""
        return [Notes.C5, Notes.E5, Notes.G5], [100, 100, 200]
    
    @staticmethod
    def error():
        """Error melody"""
        return [Notes.A4, Notes.REST, Notes.A4], [150, 50, 150]
    
    @staticmethod
    def power_on():
        """Power on melody"""
        return [Notes.C4, Notes.E4, Notes.G4, Notes.C5], [100, 100, 100, 300]
    
    @staticmethod
    def power_off():
        """Power off melody"""
        return [Notes.C5, Notes.G4, Notes.E4, Notes.C4], [100, 100, 100, 300]
