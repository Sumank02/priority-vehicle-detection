# Audio Files Directory

This directory contains pre-recorded audio files for speaker announcements.

## Required Files

- **firetruck_make_space.mp3** - Pre-recorded sound file for the announcement:
  "Firetruck Detected. Make Space."
  
- **ambulance_make_space.mp3** - Pre-recorded sound file for the announcement:
  "Ambulance Detected. Make Space."

## File Format

- **Format**: MP3 (recommended) or WAV
- **Location**: `assets/audio/{vehicle_type}_make_space.mp3`
- **Content**: Should contain the spoken text "{Vehicle} Detected. Make Space."

## Usage

The system will automatically use these files when priority vehicles (firetrucks or ambulances) are first detected. If the file is not found, the system will fall back to Text-to-Speech (TTS) to generate the announcement.

## Creating the Audio Files

You can create these files by:
1. Recording the phrase "{Vehicle} Detected. Make Space." using any audio recording software
2. Converting it to MP3 format
3. Placing it in this directory with the exact filename:
   - `firetruck_make_space.mp3` for firetrucks
   - `ambulance_make_space.mp3` for ambulances

## Note

If these files are not present, the system will use TTS (gTTS or pyttsx3) to generate the announcements automatically.

