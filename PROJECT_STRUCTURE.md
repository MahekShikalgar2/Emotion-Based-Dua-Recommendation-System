# Project Structure

```
drs/
├── audio/                          # Audio files for dua recitations
│   ├── README.md                   # Audio directory instructions
│   └── .gitkeep                    # Keep directory in git
│
├── EmotionRecognition/
│   ├── dataset/                    # Training dataset (ignored by git)
│   │   └── train/                  # Training images by emotion
│   │       ├── angry/
│   │       ├── happy/
│   │       ├── neutral/
│   │       ├── sad/
│   │       └── surprise/
│   │
│   ├── model/
│   │   ├── train_model.py         # Model training script
│   │   ├── csv_to_images.py       # Utility: CSV to images converter
│   │   └── emotion_model.h5       # Trained model (ignored by git)
│   │
│   ├── ui/
│   │   └── main_ui.py             # Main GUI application
│   │
│   ├── predict.py                  # Image prediction script
│   └── predict_webcam.py           # Webcam prediction script
│
├── .gitignore                      # Git ignore rules
├── README.md                       # Main project documentation
├── requirements.txt                # Python dependencies
├── SETUP_INSTRUCTIONS.md          # Setup and troubleshooting guide
├── enable_long_paths.ps1          # Windows long path fix script
├── fix_venv.ps1                   # Virtual environment fix script
└── INSTALLATION_FIX.md            # Installation troubleshooting

# Ignored files (not in git):
├── emotion_history.json            # User history data
├── .venv/                          # Virtual environment
└── EmotionRecognition/model/*.h5   # Trained models
```

## Key Files

- **`EmotionRecognition/ui/main_ui.py`** - Main application entry point
- **`EmotionRecognition/model/train_model.py`** - Train the emotion recognition model
- **`requirements.txt`** - Install dependencies
- **`README.md`** - Full project documentation

## Audio Files

Place audio recitations in the `audio/` directory. See `audio/README.md` for details.

