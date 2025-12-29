# Fixing TensorFlow Installation Issue (Windows Long Path Problem)

## Problem
TensorFlow installation fails with:
```
ERROR: Could not install packages due to an OSError: [Errno 2] No such file or directory: 
'...\\tensorflow\\include\\external\\com_github_grpc_grpc\\...'
```

This is caused by Windows MAX_PATH limitation (260 characters).

## Solution Options

### Option 1: Enable Long Path Support (RECOMMENDED)

**Run PowerShell as Administrator** and execute:

```powershell
New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" -Name "LongPathsEnabled" -Value 1 -PropertyType DWORD -Force
```

Then **restart your computer** and try installing again:

```powershell
cd "C:\Users\Suhana\Desktop\Projects\AI and ML\Emotion-based-dua-RS\Emotion-Based-Dua-Recommendation-System"
.\.venv\Scripts\activate
pip install -r requirements.txt
```

### Option 2: Move Project to Shorter Path

Move the project to a shorter path like:
- `C:\Projects\Emotion-Dua-RS\`
- `C:\Dev\Emotion-Dua-RS\`

Then recreate the virtual environment and install packages.

### Option 3: Use Pre-built Model (Skip Training)

If you have a pre-trained model file (`emotion_model.h5`), you can skip TensorFlow installation for training and just install the runtime dependencies:

```powershell
pip install numpy opencv-python PyQt5 pandas
```

Then use the existing model file.

## After Fixing

Once TensorFlow is installed, you can:

1. **Train the model:**
   ```powershell
   cd EmotionRecognition
   python model\train_model.py
   ```

2. **Run the GUI app:**
   ```powershell
   cd EmotionRecognition\ui
   python main_ui.py
   ```

3. **Run webcam prediction:**
   ```powershell
   cd EmotionRecognition
   python predict_webcam.py
   ```

