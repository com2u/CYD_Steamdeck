# Sound Menu Documentation

## Overview
The ESP32 CYD now includes a Sound menu that allows you to play various sound effects on your PC through the PC Service.

## Menu Structure

### Main Menu
- Setup
- System  
- **Sound** ← New menu
- Control

### Sound Sub-Menu 1
- Alarm
- Car
- Bell
- Dog
- --> (Navigate to next page)

### Sound Sub-Menu 2
- <-- (Navigate back)
- Police
- Tick
- Modem
- Applause

## How It Works

### ESP32 Side
1. Touch a sound button on the ESP32 display
2. ESP32 sends `PC_SOUND:[sound_name]` via USB debug output
3. Audio feedback plays on ESP32 speaker

### PC Service Side
1. PC Service receives the sound command
2. Looks for the sound file in `PC_Service/sound/[sound_name].mp3`
3. Plays the sound in the background using Windows Media Player
4. Logs the result

## Sound Files

The following sound files are available in `PC_Service/sound/`:
- `alarm.mp3` - Alarm sound
- `car.mp3` - Car engine sound
- `bell.mp3` - Bell chime
- `dog.mp3` - Dog barking
- `police.mp3` - Police siren
- `tick.mp3` - Clock ticking
- `modem.mp3` - Dial-up modem sound
- `applause.mp3` - Applause sound

## Technical Implementation

### ESP32 Code Changes
- Added "Sound" to main menu
- Created two sound sub-menus with navigation
- Added `execute_sound_command()` method
- Sound commands sent via `print(f"PC_SOUND:{sound_name}")`

### PC Service Changes
- New `sound_commands.py` module
- Background sound playback using PowerShell + Windows Media Player
- Sound command parsing in `service_manager.py`
- Thread-based playback to avoid blocking

### Communication Protocol
```
ESP32 → PC: PC_SOUND:Alarm
PC Service: Playing sound: Alarm
```

## Usage Example

1. Navigate to Sound menu on ESP32
2. Touch "Alarm" button
3. ESP32 plays button click sound
4. PC plays alarm.mp3 in background
5. PC Service logs: "Sound Alarm result: Playing sound: Alarm"

## Adding New Sounds

1. Place new `.mp3` file in `PC_Service/sound/` directory
2. Add button to ESP32 sound menu
3. Add sound name to button handler
4. Add function to `sound_commands.py` if needed

## Error Handling

- If sound file not found: Logs error message
- If playback fails: Continues without crashing
- Background playback: Non-blocking operation
- Thread safety: Each sound plays in separate thread
