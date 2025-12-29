# Audio Files Directory

This directory is for storing audio recitations of the duas.

## Usage

1. Place your audio files here (supported formats: `.mp3`, `.wav`, `.ogg`)
2. Update the `audio` field in the dua dictionary in `EmotionRecognition/ui/main_ui.py` to point to your audio file
3. Example: `"audio": "audio/dua_angry.mp3"`

## File Naming Convention

Suggested naming:
- `dua_angry.mp3` - For anger dua
- `dua_sad.mp3` - For sadness dua
- `dua_happy.mp3` - For happiness dua
- `dua_neutral.mp3` - For neutral dua
- `dua_surprise.mp3` - For surprise dua

## Note

Audio files are ignored by git (see `.gitignore`) to keep the repository size manageable. You can add your own audio files locally.

