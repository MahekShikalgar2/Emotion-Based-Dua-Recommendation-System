# 🌙 Noor-e-Dua – Light of Supplication

> *Finding peace through duas based on your emotions*

---

## 📌 Overview
Emotions deeply impact mental well-being. **Noor-e-Dua – Light of Supplication** uses **Artificial Intelligence and Computer Vision** to detect facial emotions and suggest **emotion-appropriate Duas**, promoting peace, positivity, and mindfulness through technology.

---

## ✨ Key Features
- 😊 **Facial Emotion Detection** using Deep Learning (webcam)
- 📝 **Text-based emotion input** for days you don't want to use the camera
- 🕌 **Emotion-wise Islamic Dua recommendation** with title, Arabic, translation, meaning, and reference
- 🔊 **Optional audio recitation button** (plug in your own audio files)
- 📜 **Emotion history** with time and dua shown
- 👍👎 **Feedback buttons** to mark a dua as helpful or not
- 🧠 Beginner-friendly, well-structured Python code

---

## 😄 Supported Emotions
| Emotion | Description |
|-------|-------------|
| 😊 Happy | Positive & joyful state |
| 😢 Sad | Emotional distress |
| 😠 Angry | High emotional intensity |
| 😐 Neutral | Balanced emotion |
| 😲 Surprise | Sudden emotional reaction |

---

## 🛠️ Tech Stack
- **Python**
- **OpenCV**
- **TensorFlow / Keras**
- **NumPy & Pandas**
- **Emotion Dataset**

---

## 📦 Installation & Setup

### Prerequisites
- Python 3.8 or higher
- Webcam (for real-time detection)

### Step 1: Install Dependencies

**Option A: Using pip (Recommended)**
```powershell
pip install -r requirements.txt
```

**Option B: If you encounter Windows Long Path issues**
1. Run PowerShell as Administrator and execute:
```powershell
New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" -Name "LongPathsEnabled" -Value 1 -PropertyType DWORD -Force
```
2. Restart your computer
3. Then run: `pip install -r requirements.txt`

### Step 2: Train the Model (First Time Only)

The model needs to be trained before use. Navigate to the EmotionRecognition directory:

```powershell
cd EmotionRecognition
python model\train_model.py
```

This will:
- Load the training dataset from `EmotionRecognition/dataset/train/`
- Train a CNN model for emotion recognition
- Save the model as `EmotionRecognition/model/emotion_model.h5`

**Note:** Training may take 10-30 minutes depending on your hardware.

---

## 🚀 How to Run

### Option 1: Run GUI Application (Recommended)

The GUI provides a user-friendly interface with camera feed and Dua recommendations:

```powershell
cd EmotionRecognition\ui
python main_ui.py
```

**Features:**
- Real-time webcam emotion detection
- Text-based emotion description input
- Rich dua card (Arabic, translation, meaning, reference)
- Simple feedback and history tracking
- Start/Pause/Exit controls

### Option 2: Run Webcam Prediction (Command Line)

For a simpler command-line interface:

```powershell
cd EmotionRecognition
python predict_webcam.py
```

Press `q` to quit.

### Option 3: Run Image Prediction

To predict emotions from a single image:

```powershell
cd EmotionRecognition
python predict.py
```

---

## 🚀 How It Works
1. Capture or load a facial image  
2. Detect emotion using a trained deep learning model  
3. Map detected emotion to a relevant Dua  
4. Display Dua for emotional support  

---

## 🎯 Use Cases
- Mental health & emotional well-being tools  
- Faith-based AI systems  
- Educational AI & ML projects  
- Ethical AI research initiatives  

---

## 🔮 Future Enhancements
- 🌙 Deeper dua library with more categories
- 📱 Web & Mobile app integration  
- 🗣️ Smarter, NLP-based emotion understanding  
- 🌍 Multi-language dua translations  

---
