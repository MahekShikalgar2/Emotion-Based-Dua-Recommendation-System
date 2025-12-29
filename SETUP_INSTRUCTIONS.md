# 🔧 Setup Instructions - Fix Virtual Environment & TensorFlow

## Problem
Your virtual environment is broken and TensorFlow installation is corrupted.

## Solution: Recreate Virtual Environment

### Step 1: Deactivate Current Virtual Environment
```powershell
deactivate
```

### Step 2: Remove Broken Virtual Environment
```powershell
Remove-Item -Recurse -Force .venv
```

### Step 3: Create New Virtual Environment
```powershell
python -m venv .venv
```

### Step 4: Activate Virtual Environment
```powershell
.\.venv\Scripts\Activate.ps1
```

### Step 5: Upgrade pip
```powershell
python -m pip install --upgrade pip
```

### Step 6: Install Dependencies

**Option A: Install all at once (may fail on Windows Long Path)**
```powershell
pip install -r requirements.txt
```

**Option B: Install one by one (recommended if Option A fails)**
```powershell
pip install numpy
pip install opencv-python
pip install PyQt5
pip install pandas
pip install tensorflow==2.15.0
```

**If you get Windows Long Path errors:**
1. Run PowerShell **as Administrator**
2. Execute: `.\enable_long_paths.ps1`
3. **Restart your computer**
4. Then try installing again

### Step 7: Verify Installation
```powershell
python -c "import tensorflow as tf; print('TensorFlow version:', tf.__version__)"
python -c "import cv2; print('OpenCV version:', cv2.__version__)"
python -c "import PyQt5; print('PyQt5 installed')"
```

### Step 8: Train the Model
```powershell
cd EmotionRecognition
python model\train_model.py
```

### Step 9: Run the Application
```powershell
cd EmotionRecognition\ui
python main_ui.py
```

---

## Quick Fix Script

Alternatively, you can run the automated fix script:
```powershell
.\fix_venv.ps1
```

This script will:
- ✅ Deactivate current venv
- ✅ Remove broken .venv folder
- ✅ Create new virtual environment
- ✅ Activate it
- ✅ Upgrade pip
- ✅ Install all dependencies

---

## Troubleshooting

### Error: "ModuleNotFoundError: No module named 'tensorflow.python'"
- **Solution**: TensorFlow installation is corrupted. Reinstall it:
  ```powershell
  pip uninstall tensorflow
  pip install tensorflow==2.15.0
  ```

### Error: "Fatal error in launcher: Unable to create process"
- **Solution**: Virtual environment is pointing to wrong Python path. Recreate venv (Steps 1-4 above).

### Error: Windows Long Path issues
- **Solution**: Enable long paths (see Option B in Step 6) or move project to shorter path like `C:\Projects\DRS\`

### Error: "pip: command not found"
- **Solution**: Make sure virtual environment is activated (you should see `(.venv)` in your prompt).

