# Audio Playback Setup

## Issue
The application uses `.mp4` audio files, which require additional setup to play.

## Solution Options

### Option 1: Install FFmpeg (Recommended for .mp4 files)

**Windows:**
1. Download FFmpeg from: https://www.gyan.dev/ffmpeg/builds/
2. Extract and add to PATH, or place `ffmpeg.exe` in the project folder
3. Restart the application

**Or use chocolatey:**
```powershell
choco install ffmpeg
```

### Option 2: Convert Audio Files to .mp3 or .wav

Convert your `.mp4` files to `.mp3` or `.wav` format (which don't require ffmpeg):

**Using FFmpeg (if you have it):**
```powershell
ffmpeg -i audio/angry.mp4 audio/angry.mp3
ffmpeg -i audio/sad.mp4 audio/sad.mp3
ffmpeg -i audio/happy.mp4 audio/happy.mp3
ffmpeg -i audio/neutral.mp4 audio/neutral.mp3
ffmpeg -i audio/surprise.mp4 audio/surprise.mp3
```

**Using online converter:**
- Upload your .mp4 files to an online converter
- Download as .mp3 or .wav
- Replace files in the `audio/` folder

### Option 3: Update Code to Use Different Format

If you convert files, update the file extensions in `EmotionRecognition/ui/main_ui.py`:
- Change `"angry.mp4"` to `"angry.mp3"` (or `.wav`)
- Do the same for all other emotions

## Current Status

The application uses `pydub` library which supports:
- ✅ .mp3 (no ffmpeg needed)
- ✅ .wav (no ffmpeg needed)  
- ⚠️ .mp4 (requires ffmpeg)

## Installation

Make sure you have the required packages:
```powershell
pip install pydub simpleaudio
```

