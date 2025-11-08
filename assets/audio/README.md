# Audio Files Directory

This directory contains pre-recorded audio files for speaker announcements.

## Required File

- **firetruck_make_space.mp3** - Pre-recorded sound file for the announcement:
  "Firetruck Detected. Make Space."

## File Format

- **Format**: MP3 (recommended) or WAV
- **Location**: `assets/audio/firetruck_make_space.mp3`
- **Content**: Should contain the spoken text "Firetruck Detected. Make Space."

## Usage

The system will automatically use this file when a firetruck is first detected. If the file is not found, the system will fall back to Text-to-Speech (TTS) to generate the announcement.

## Creating the Audio File

You can create this file by:
1. Recording the phrase "Firetruck Detected. Make Space." using any audio recording software
2. Converting it to MP3 format
3. Placing it in this directory with the exact filename: `firetruck_make_space.mp3`

## Note

If this file is not present, the system will use TTS (gTTS or pyttsx3) to generate the announcement automatically.

