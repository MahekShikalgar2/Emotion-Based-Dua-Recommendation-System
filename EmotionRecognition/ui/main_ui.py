import sys
import os
import json
from datetime import datetime

import cv2
import numpy as np

from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QFrame,
    QScrollArea,
    QTextEdit,
)
from PyQt5.QtGui import QFont, QImage, QPixmap
from PyQt5.QtCore import Qt, QTimer, QUrl
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent

from tensorflow.keras.models import load_model

# Audio playback using pyglet (supports .mp4 on Windows without FFmpeg)
try:
    import pyglet
    import threading
    PYGLET_AVAILABLE = True
except ImportError:
    PYGLET_AVAILABLE = False
    print("⚠️ pyglet not available, audio playback may not work")
    print("   Install: pip install pyglet")

class EmotionDuaApp(QMainWindow):
    def __init__(self):
        super().__init__()

        # App window title (rebranded)
        self.setWindowTitle("Noor-e-Dua – Peace in Every Emotion")
        self.setGeometry(80, 80, 1300, 800)

        # ================= PATHS & STATE =================
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.join(script_dir, '..', '..')
        model_path = os.path.join(project_root, 'EmotionRecognition', 'model', 'emotion_model.h5')
        self.history_path = os.path.join(project_root, 'emotion_history.json')
        self.audio_dir = os.path.join(project_root, 'audio')

        self.current_emotion = None
        self.current_dua = None
        self.input_mode = "camera"  # or "text"
        self.history = []

        self._load_history()

        # ================= LOAD MODEL =================
        self.model = load_model(model_path, compile=False)
        print("✅ Emotion model loaded successfully")

        self.classes = ['angry', 'happy', 'neutral', 'sad', 'surprise']

        # ================= FACE DETECTOR =================
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )

        # ================= CAMERA & TIMER =================
        self.cap = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)

        # ================= AUDIO PLAYER =================
        # Use pyglet for reliable audio playback (supports .mp4 on Windows)
        self.current_audio_path = None
        self.is_playing_audio = False
        self.audio_player = None
        self.audio_thread = None
        # Timer to check audio status and update button
        self.audio_status_timer = QTimer()
        self.audio_status_timer.timeout.connect(self.check_audio_status)

        # ================= UI =================
        self.init_ui()

    # --------------------------------------------------
    def init_ui(self):
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(24, 16, 24, 16)
        main_layout.setSpacing(16)

        # ===== Global background =====
        main_widget.setStyleSheet(
            """
            QWidget {
                background-color: #f7f5f0;
                font-family: Segoe UI, Arial, sans-serif;
            }
            QLabel#TitleLabel {
                color: #16423C;
                font-size: 26px;
                font-weight: 600;
            }
            QLabel#TaglineLabel {
                color: #5f6f68;
                font-size: 13px;
            }
            QFrame#Card {
                background-color: #ffffff;
                border-radius: 14px;
                border: 1px solid #e2ded2;
            }
            QPushButton {
                border-radius: 10px;
                padding: 10px 18px;
                font-size: 14px;
            }
            QPushButton#PrimaryButton {
                background-color: #2f7d5b;
                color: white;
            }
            QPushButton#PrimaryButton:hover {
                background-color: #2a6f51;
            }
            QPushButton#SecondaryButton {
                background-color: #e6f2ec;
                color: #244f3b;
            }
            QPushButton#DangerButton {
                background-color: #fbe5e5;
                color: #9c2b2b;
            }
            QLineEdit {
                border-radius: 10px;
                padding: 8px 10px;
                border: 1px solid #d0c7b5;
                background-color: #fdfaf5;
            }
            QTextEdit {
                border-radius: 10px;
                padding: 8px 10px;
                border: 1px solid #d0c7b5;
                background-color: #fdfaf5;
                font-size: 13px;
            }
            QTextEdit:focus {
                border: 2px solid #2f7d5b;
                background-color: #ffffff;
            }
            """
        )

        # ===== Header =====
        header = QFrame()
        header_layout = QVBoxLayout()

        title = QLabel("🌙 Noor-e-Dua – Peace in Every Emotion")
        title.setObjectName("TitleLabel")
        title.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        tagline = QLabel("Finding peace through duas based on your emotions")
        tagline.setObjectName("TaglineLabel")
        tagline.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        header_layout.addWidget(title)
        header_layout.addWidget(tagline)
        header.setLayout(header_layout)

        # ===== Content area (Left and Right) =====
        content_layout = QHBoxLayout()
        content_layout.setSpacing(20)

        # -------- LEFT: Camera + Text Input + History (Scrollable) --------
        left_panel = QFrame()
        left_panel.setObjectName("Card")
        
        # Create scrollable area for left panel
        left_scroll = QScrollArea()
        left_scroll.setWidgetResizable(True)
        left_scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                background-color: #f0ede6;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #c4b8a0;
                border-radius: 6px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #a89b83;
            }
        """)
        
        left_content_widget = QWidget()
        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(16, 16, 16, 16)
        left_layout.setSpacing(16)

        # ===== CAMERA SECTION (Full width of left panel) =====
        camera_title = QLabel("📷 Camera Detection")
        camera_title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        camera_title.setStyleSheet("color: #244f3b; margin-bottom: 8px; font-size: 16px;")

        # Camera preview - Fixed size to prevent resizing
        self.camera_label = QLabel("Camera Off")
        self.camera_label.setFixedSize(850, 520)  # Increased width and height
        self.camera_label.setAlignment(Qt.AlignCenter)
        self.camera_label.setStyleSheet(
            "background-color: #111; color: #f5f5f5; "
            "border-radius: 12px; border: 1px solid #374a3f;"
        )
        self.camera_label.setScaledContents(True)  # Scale contents to fit fixed size

        # Camera controls
        btn_layout = QHBoxLayout()
        self.start_btn = QPushButton("▶ Start camera")
        self.start_btn.setObjectName("PrimaryButton")

        self.pause_btn = QPushButton("⏸ Pause")
        self.pause_btn.setObjectName("SecondaryButton")

        self.exit_btn = QPushButton("❌ Exit")
        self.exit_btn.setObjectName("DangerButton")

        self.start_btn.clicked.connect(self.start_camera)
        self.pause_btn.clicked.connect(self.stop_camera)
        self.exit_btn.clicked.connect(self.close)

        btn_layout.addWidget(self.start_btn)
        btn_layout.addWidget(self.pause_btn)
        btn_layout.addWidget(self.exit_btn)
        btn_layout.addStretch()

        # ===== TEXT INPUT SECTION (Toggleable) =====
        text_header_layout = QHBoxLayout()
        text_title = QLabel("✍️ Type Mood")
        text_title.setFont(QFont("Segoe UI", 15, QFont.Bold))
        text_title.setStyleSheet("color: #244f3b; margin-bottom: 8px; font-size: 15px;")
        
        self.text_toggle_btn = QPushButton("✍️ Type Mood")
        self.text_toggle_btn.setObjectName("PrimaryButton")
        self.text_toggle_btn.setMaximumWidth(160)
        self.text_toggle_btn.clicked.connect(self.toggle_text_input)
        
        text_header_layout.addWidget(self.text_toggle_btn)
        text_header_layout.addStretch()

        # Text emotion input - Initially hidden, toggleable
        self.text_input = QTextEdit()
        self.text_input.setPlaceholderText(
            "How are you feeling today? (e.g., anxious, sad, grateful, happy, angry)"
        )
        self.text_input.setMinimumHeight(100)
        self.text_input.setMaximumHeight(120)
        self.text_input.setEnabled(True)
        self.text_input.setAcceptRichText(False)
        self.text_input.setFocusPolicy(Qt.StrongFocus)
        self.text_input.setVisible(False)  # Initially hidden
        self.text_input.setStyleSheet("font-size: 14px;")

        self.text_submit_btn = QPushButton("✨ Find Dua from text")
        self.text_submit_btn.setObjectName("PrimaryButton")
        self.text_submit_btn.clicked.connect(self.on_text_submit)
        self.text_submit_btn.setVisible(False)  # Initially hidden

        # ===== HISTORY SECTION =====
        history_header_layout = QHBoxLayout()
        history_title = QLabel("📜 Recent History")
        history_title.setFont(QFont("Segoe UI", 15, QFont.Bold))
        history_title.setStyleSheet("color: #244f3b; margin-top: 16px; margin-bottom: 8px; font-size: 15px;")
        
        self.history_toggle_btn = QPushButton("📜 Hide History")
        self.history_toggle_btn.setObjectName("SecondaryButton")
        self.history_toggle_btn.setMaximumWidth(140)
        self.history_toggle_btn.clicked.connect(self.toggle_history)
        
        self.history_refresh_btn = QPushButton("🔄 Refresh")
        self.history_refresh_btn.setObjectName("SecondaryButton")
        self.history_refresh_btn.setMaximumWidth(110)
        self.history_refresh_btn.clicked.connect(self.refresh_history)
        
        history_header_layout.addWidget(history_title)
        history_header_layout.addWidget(self.history_toggle_btn)
        history_header_layout.addWidget(self.history_refresh_btn)
        history_header_layout.addStretch()

        self.history_label = QLabel("No history yet.")
        self.history_label.setWordWrap(True)
        self.history_label.setStyleSheet("color: #5f6f68; font-size: 13px; padding: 8px;")
        self.history_label.setAlignment(Qt.AlignTop)
        self.history_label.setTextFormat(Qt.RichText)  # Enable HTML formatting
        self.history_label.setVisible(True)  # Initially visible

        # Add all to left layout
        left_layout.addWidget(camera_title)
        left_layout.addWidget(self.camera_label)
        left_layout.addLayout(btn_layout)
        
        left_layout.addLayout(text_header_layout)
        left_layout.addWidget(self.text_input)
        left_layout.addWidget(self.text_submit_btn)
        
        left_layout.addLayout(history_header_layout)
        left_layout.addWidget(self.history_label)
        left_layout.addStretch()
        
        left_content_widget.setLayout(left_layout)
        left_scroll.setWidget(left_content_widget)
        left_panel_layout = QVBoxLayout()
        left_panel_layout.setContentsMargins(0, 0, 0, 0)
        left_panel_layout.addWidget(left_scroll)
        left_panel.setLayout(left_panel_layout)

        # -------- RIGHT: Dua card + feedback + history toggle --------
        right_panel = QFrame()
        right_panel.setObjectName("Card")
        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(20, 20, 20, 20)
        right_layout.setSpacing(12)

        self.emotion_label = QLabel("Emotion: ---")
        self.emotion_label.setFont(QFont("Segoe UI", 20, QFont.Bold))
        self.emotion_label.setStyleSheet(
            "color: #244f3b; padding: 14px; background-color: #e6f2ec; "
            "border-radius: 8px; margin-bottom: 4px; font-size: 20px;"
        )

        # Scrollable dua content area
        dua_scroll = QScrollArea()
        dua_scroll.setWidgetResizable(True)
        dua_scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                background-color: #f0ede6;
                width: 10px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background-color: #c4b8a0;
                border-radius: 5px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #a89b83;
            }
        """)
        
        dua_content_widget = QWidget()
        dua_content_layout = QVBoxLayout()
        dua_content_layout.setContentsMargins(0, 0, 0, 0)
        dua_content_layout.setSpacing(12)

        # Dua fields - BIGGER TEXT
        self.dua_title_label = QLabel("Dua will appear here")
        self.dua_title_label.setFont(QFont("Segoe UI", 20, QFont.Bold))
        self.dua_title_label.setStyleSheet("color: #1f3b30; margin-bottom: 8px; font-size: 20px;")

        self.dua_arabic_label = QLabel("")
        self.dua_arabic_label.setStyleSheet(
            "font-size: 32px; color: #16423C; font-family: 'Scheherazade', 'Traditional Arabic', serif; "
            "padding: 18px; background-color: #f9f7f2; border-radius: 8px; margin: 6px 0;"
        )
        self.dua_arabic_label.setWordWrap(True)
        self.dua_arabic_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        self.dua_english_pronunciation_label = QLabel("")
        self.dua_english_pronunciation_label.setStyleSheet(
            "color: #4a5d52; font-size: 18px; font-style: italic; padding: 10px 0;"
        )
        self.dua_english_pronunciation_label.setWordWrap(True)

        self.dua_hindi_pronunciation_label = QLabel("")
        self.dua_hindi_pronunciation_label.setStyleSheet(
            "color: #5a6b5f; font-size: 18px; font-style: italic; padding: 10px 0;"
        )
        self.dua_hindi_pronunciation_label.setWordWrap(True)

        self.dua_translation_label = QLabel("")
        self.dua_translation_label.setStyleSheet(
            "color: #3e4b45; font-size: 18px; padding: 14px; background-color: #f5f3ed; "
            "border-radius: 6px; margin: 6px 0;"
        )
        self.dua_translation_label.setWordWrap(True)

        self.dua_meaning_label = QLabel("")
        self.dua_meaning_label.setStyleSheet("color: #6a746e; font-size: 17px; padding: 10px 0;")
        self.dua_meaning_label.setWordWrap(True)

        self.dua_reference_label = QLabel("")
        self.dua_reference_label.setStyleSheet(
            "color: #8b7c4b; font-size: 16px; padding-top: 12px; border-top: 1px solid #e2ded2;"
        )
        self.dua_reference_label.setWordWrap(True)

        dua_content_layout.addWidget(self.dua_title_label)
        dua_content_layout.addWidget(self.dua_arabic_label)
        dua_content_layout.addWidget(self.dua_english_pronunciation_label)
        dua_content_layout.addWidget(self.dua_hindi_pronunciation_label)
        dua_content_layout.addWidget(self.dua_translation_label)
        dua_content_layout.addWidget(self.dua_meaning_label)
        dua_content_layout.addWidget(self.dua_reference_label)
        dua_content_layout.addStretch()
        
        dua_content_widget.setLayout(dua_content_layout)
        dua_scroll.setWidget(dua_content_widget)

        # Audio + feedback
        controls_row = QHBoxLayout()

        self.audio_btn = QPushButton("▶ Listen")
        self.audio_btn.setObjectName("SecondaryButton")
        self.audio_btn.clicked.connect(self.toggle_audio)
        self.audio_btn.setEnabled(False)

        feedback_container = QHBoxLayout()
        feedback_label = QLabel("Was this helpful?")
        feedback_label.setStyleSheet("color: #5a615a; font-size: 15px;")
        feedback_label.setFont(QFont("Segoe UI", 15))

        self.feedback_yes_btn = QPushButton("👍 Yes")
        self.feedback_no_btn = QPushButton("👎 No")
        self.feedback_yes_btn.setObjectName("SecondaryButton")
        self.feedback_no_btn.setObjectName("SecondaryButton")

        self.feedback_yes_btn.clicked.connect(lambda: self.on_feedback(True))
        self.feedback_no_btn.clicked.connect(lambda: self.on_feedback(False))

        feedback_container.addWidget(feedback_label)
        feedback_container.addWidget(self.feedback_yes_btn)
        feedback_container.addWidget(self.feedback_no_btn)
        feedback_container.addStretch()

        controls_row.addWidget(self.audio_btn)
        controls_row.addLayout(feedback_container)

        right_layout.addWidget(self.emotion_label)
        right_layout.addSpacing(8)
        right_layout.addWidget(dua_scroll)
        right_layout.addSpacing(8)
        right_layout.addLayout(controls_row)

        right_panel.setLayout(right_layout)

        content_layout.addWidget(left_panel, stretch=3)
        content_layout.addWidget(right_panel, stretch=3)

        # ===== Footer =====
        footer = QLabel('"Verily, in the remembrance of Allah do hearts find rest." (Qur\'an 13:28)')
        footer.setAlignment(Qt.AlignCenter)
        footer.setStyleSheet("color: #8c7f5a; font-size: 11px;")

        # Add everything to main layout
        main_layout.addWidget(header)
        main_layout.addLayout(content_layout)  # Left (Camera + History) and Right (Dua display)
        main_layout.addWidget(footer)

        self._refresh_history_view()

        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

    # --------------------------------------------------
    def start_camera(self):
        if self.cap is None:
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                print("❌ Camera not found")
                self.cap = None
                return
            self.timer.start(30)
            print("▶ Camera started")

    # --------------------------------------------------
    def stop_camera(self):
        self.timer.stop()
        if self.cap:
            self.cap.release()
            self.cap = None
            self.camera_label.setText("Camera Off")
            print("⏸ Camera stopped")

    # --------------------------------------------------
    def update_frame(self):
        if self.cap is None:
            return

        ret, frame = self.cap.read()
        if not ret:
            return

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)

        for (x, y, w, h) in faces:
            roi = gray[y:y + h, x:x + w]
            roi = cv2.resize(roi, (48, 48))
            roi = roi.reshape(1, 48, 48, 1).astype("float32") / 255.0

            preds = self.model.predict(roi, verbose=0)
            emotion = self.classes[np.argmax(preds)]

            dua = self.get_dua_for_emotion(emotion)
            self.show_dua(dua, source_emotion=emotion)

            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(
                frame,
                emotion,
                (x, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.9,
                (0, 255, 0),
                2,
            )

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        bytes_per_line = ch * w
        qt_img = QImage(rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
        
        # Convert to pixmap - setScaledContents(True) will handle scaling to fixed size
        pixmap = QPixmap.fromImage(qt_img)
        self.camera_label.setPixmap(pixmap)

    # --------------------------------------------------
    def get_dua_for_emotion(self, emotion: str):
        """Return structured dua info for a given emotion key."""
        emotion = (emotion or "").lower()

        # Helper function to get audio path if file exists
        def get_audio_path(filename):
            audio_path = os.path.join(self.audio_dir, filename)
            if os.path.exists(audio_path):
                return audio_path
            return None

        duas = {
            "angry": {
                "title": "For calming anger",
                "arabic": "اللَّهُمَّ اغْفِرْ لِي وَأَذْهِبْ غَيْظَ قَلْبِي",
                "english_pronunciation": "Allahumma ighfir li wa adhib ghayza qalbi",
                "hindi_pronunciation": "अल्लाहुम्मा इग़्फिर ली व अज़्हिब ग़ैज़ा क़ल्बी",
                "translation": "O Allah, forgive me and remove the rage from my heart.",
                "meaning": "A short supplication to soften the heart and calm intense feelings.",
                "reference": "A general supplication consistent with Islamic teachings.",
                "audio": get_audio_path("angry.mp4"),
            },
            "sad": {
                "title": "When feeling sadness or worry",
                "arabic": "اللَّهُمَّ إِنِّي أَعُوذُ بِكَ مِنَ الْهَمِّ وَالْحَزَنِ",
                "english_pronunciation": "Allahumma inni a'udhu bika min al-hammi wal-hazan",
                "hindi_pronunciation": "अल्लाहुम्मा इन्नी आउज़ु बिका मिन अल-हम्मि वल-हज़न",
                "translation": "O Allah, I seek refuge in You from anxiety and sorrow.",
                "meaning": "A dua to seek relief from emotional burdens and sadness.",
                "reference": "Sahih al-Bukhari",
                "audio": get_audio_path("sad.mp4"),
            },
            "happy": {
                "title": "Gratefulness for blessings",
                "arabic": "ٱلْحَمْدُ لِلَّٰهِ الَّذِي بِنِعْمَتِهِ تَتِمُّ ٱلصَّالِحَاتُ",
                "english_pronunciation": "Alhamdu lillahi alladhi bi ni'matihi tatimmu as-salihat",
                "hindi_pronunciation": "अल-हम्दु लिल्लाहि अल्लज़ी बि नि'मतिही ततिम्मु अस-सालिहात",
                "translation": "All praise is for Allah by whose favor good works are completed.",
                "meaning": "A remembrance to show gratitude when things go well.",
                "reference": "Sunan Ibn Majah",
                "audio": get_audio_path("happy.mp4"),
            },
            "neutral": {
                "title": "Seeking knowledge and guidance",
                "arabic": "رَبِّ زِدْنِي عِلْمًا",
                "english_pronunciation": "Rabbi zidni ilma",
                "hindi_pronunciation": "रब्बी ज़िद्नी इल्मा",
                "translation": "My Lord, increase me in knowledge.",
                "meaning": "A simple dua for growth, clarity and beneficial knowledge.",
                "reference": "Qur'an 20:114",
                "audio": get_audio_path("neutral.mp4"),
            },
            "surprise": {
                "title": "For moments of amazement",
                "arabic": "سُبْحَانَ اللَّهِ وَبِحَمْدِهِ",
                "english_pronunciation": "Subhanallahi wa bihamdihi",
                "hindi_pronunciation": "सुब्हानल्लाहि व बिहम्दिही",
                "translation": "Glory and praise be to Allah.",
                "meaning": "A light dhikr suitable when something unexpected happens.",
                "reference": "Sahih Muslim",
                "audio": get_audio_path("surprise.mp4"),
            },
        }

        return duas.get(
            emotion,
            {
                "title": "A gentle remembrance",
                "arabic": "سُبْحَانَ اللَّهِ وَبِحَمْدِهِ سُبْحَانَ اللَّهِ الْعَظِيمِ",
                "english_pronunciation": "Subhanallahi wa bihamdihi, subhanallahi al-azeem",
                "hindi_pronunciation": "सुब्हानल्लाहि व बिहम्दिही, सुब्हानल्लाहि अल-अज़ीम",
                "translation": "Glory and praise be to Allah, glory be to Allah the Most Great.",
                "meaning": "A general dhikr that brings peace to the heart.",
                "reference": "Sahih al-Bukhari",
                "audio": get_audio_path("normal.mp4"),
            },
        )

    # --------------------------------------------------
    # UI helpers & new features
    # --------------------------------------------------
    # Mode switching removed - both camera and text are always available

    def on_text_submit(self):
        text = (self.text_input.toPlainText() or "").strip().lower()
        if not text:
            self.emotion_label.setText("Emotion: (please describe how you feel)")
            return

        emotion = self._map_text_to_emotion(text)
        dua = self.get_dua_for_emotion(emotion)
        self.show_dua(dua, source_emotion=emotion or text)

    def show_dua(self, dua: dict, source_emotion: str):
        self.current_dua = dua
        self.current_emotion = source_emotion

        label = (source_emotion or "---").upper()
        self.emotion_label.setText(f"Emotion: {label}")

        self.dua_title_label.setText(dua.get("title", ""))
        self.dua_arabic_label.setText(dua.get("arabic", ""))
        
        # English pronunciation
        eng_pron = dua.get("english_pronunciation", "")
        if eng_pron:
            self.dua_english_pronunciation_label.setText(f"English: {eng_pron}")
            self.dua_english_pronunciation_label.setVisible(True)
        else:
            self.dua_english_pronunciation_label.setVisible(False)
        
        # Hindi pronunciation
        hindi_pron = dua.get("hindi_pronunciation", "")
        if hindi_pron:
            self.dua_hindi_pronunciation_label.setText(f"Hindi: {hindi_pron}")
            self.dua_hindi_pronunciation_label.setVisible(True)
        else:
            self.dua_hindi_pronunciation_label.setVisible(False)
        
        self.dua_translation_label.setText(dua.get("translation", ""))
        self.dua_meaning_label.setText(dua.get("meaning", ""))
        self.dua_reference_label.setText(f"Reference: {dua.get('reference', '')}")

        audio_path = dua.get("audio")
        if audio_path and os.path.exists(audio_path):
            self.current_audio_path = audio_path
            self.audio_btn.setEnabled(True)
            print(f"✅ Audio file loaded: {audio_path}")
        else:
            self.current_audio_path = None
            self.stop_audio()
            self.audio_btn.setEnabled(False)
            if audio_path:
                print(f"⚠️ Audio file not found: {audio_path}")
        
        # Reset button state
        if not self.is_playing_audio:
            self.audio_btn.setText("▶ Listen")

        # Record history entry
        self._add_history_entry(source_emotion, dua)

    def stop_audio(self):
        """Stop any currently playing audio"""
        self.audio_status_timer.stop()  # Stop status checking timer
        if self.audio_player:
            try:
                self.audio_player.pause()
                self.audio_player.delete()
                self.audio_player = None
            except:
                pass
        self.is_playing_audio = False
    
    def check_audio_status(self):
        """Check if audio is still playing and update button (called from main thread)"""
        if self.audio_player:
            if not self.audio_player.playing and self.is_playing_audio:
                # Audio finished
                self.is_playing_audio = False
                self.audio_btn.setText("▶ Listen")
                self.audio_status_timer.stop()
                print("✅ Audio finished")
        else:
            # No player, stop timer
            if self.is_playing_audio:
                self.is_playing_audio = False
                self.audio_btn.setText("▶ Listen")
            self.audio_status_timer.stop()
    
    def play_audio_in_thread(self, audio_path):
        """Play audio in a separate thread to avoid blocking UI"""
        try:
            if not PYGLET_AVAILABLE:
                print("❌ pyglet not available. Please install: pip install pyglet")
                self.is_playing_audio = False
                # Use QTimer to update UI from main thread
                QTimer.singleShot(0, lambda: self.audio_btn.setText("▶ Listen"))
                return
            
            # Create pyglet player (supports .mp4, .mp3, .wav, etc.)
            try:
                source = pyglet.media.load(audio_path)
                self.audio_player = pyglet.media.Player()
                self.audio_player.queue(source)
                self.audio_player.play()
                
                # Wait for audio to finish (simplified approach)
                # Timer is already started from main thread in toggle_audio()
                import time
                while self.is_playing_audio and self.audio_player and self.audio_player.playing:
                    time.sleep(0.1)
                    # Update pyglet clock to keep playback going
                    pyglet.clock.tick()
                
            except Exception as e:
                print(f"❌ Failed to load/play audio: {e}")
                self.is_playing_audio = False
                # Use QTimer to update UI from main thread
                QTimer.singleShot(0, lambda: self.audio_btn.setText("▶ Listen"))
                
        except Exception as e:
            print(f"❌ Audio playback error: {e}")
            self.is_playing_audio = False
            # Use QTimer to update UI from main thread
            QTimer.singleShot(0, lambda: self.audio_btn.setText("▶ Listen"))
    
    def toggle_audio(self):
        """Toggle audio playback using pyglet (plays within the app, supports .mp4 on Windows)"""
        if not self.current_audio_path or not os.path.exists(self.current_audio_path):
            print("⚠️ No audio file available")
            return

        if not PYGLET_AVAILABLE:
            print("❌ pyglet not available. Please install: pip install pyglet")
            self.audio_btn.setEnabled(False)
            return

        try:
            if self.is_playing_audio:
                # Stop audio
                self.stop_audio()
                self.audio_btn.setText("▶ Listen")
                print("⏸ Audio stopped")
            else:
                # Play audio in separate thread
                self.is_playing_audio = True
                self.audio_btn.setText("⏸ Pause")
                print(f"▶ Playing audio: {self.current_audio_path}")
                
                # Start timer to check audio status (must be started from main thread)
                self.audio_status_timer.start(200)  # Check every 200ms
                
                # Start audio in background thread
                self.audio_thread = threading.Thread(
                    target=self.play_audio_in_thread,
                    args=(self.current_audio_path,),
                    daemon=True
                )
                self.audio_thread.start()
        except Exception as e:
            print(f"❌ Audio playback error: {e}")
            self.audio_btn.setEnabled(False)

    def on_feedback(self, helpful: bool):
        if not self.current_dua:
            return

        # Append feedback to last history item if any
        if self.history:
            self.history[-1]["helpful"] = bool(helpful)
            self._save_history()
            self._refresh_history_view()

        msg = "Alhamdulillah 🌙" if helpful else "Noted. May Allah ease your heart."
        self.dua_meaning_label.setText(
            f"{self.current_dua.get('meaning', '')}\n\n{msg}"
        )

    def toggle_history(self):
        """Toggle visibility of history section only (doesn't affect camera)"""
        visible = not self.history_label.isVisible()
        self.history_label.setVisible(visible)
        self.history_toggle_btn.setText("📜 Show History" if not visible else "📜 Hide History")

    def toggle_text_input(self):
        """Toggle visibility of text input section"""
        visible = not self.text_input.isVisible()
        self.text_input.setVisible(visible)
        self.text_submit_btn.setVisible(visible)
        self.text_toggle_btn.setText("✍️ Hide Mood Input" if visible else "✍️ Type Mood")
        if visible:
            self.text_input.setFocus()

    def refresh_history(self):
        """Reload and refresh history from file"""
        self._load_history()
        self._refresh_history_view()

    # History toggle removed - history is always visible in left panel

    # --------------------------------------------------
    # History & persistence
    # --------------------------------------------------
    def _load_history(self):
        try:
            if os.path.exists(self.history_path):
                with open(self.history_path, "r", encoding="utf-8") as f:
                    self.history = json.load(f)
        except Exception:
            self.history = []

    def _save_history(self):
        try:
            with open(self.history_path, "w", encoding="utf-8") as f:
                json.dump(self.history, f, ensure_ascii=False, indent=2)
        except Exception:
            # Keep the app running even if disk write fails
            pass

    def _add_history_entry(self, emotion: str, dua: dict):
        entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "emotion": emotion,
            "dua_title": dua.get("title", ""),
        }
        self.history.append(entry)
        # Keep only latest 20 entries
        self.history = self.history[-20:]
        self._save_history()
        self._refresh_history_view()

    def _refresh_history_view(self):
        if not self.history:
            self.history_label.setText("No history yet.")
            return

        lines = []
        for item in reversed(self.history[-10:]):  # Show last 10 entries
            timestamp = item.get('timestamp', '')
            emotion = item.get('emotion', '').upper()
            dua_title = item.get('dua_title', '')
            line = f"<div style='padding: 6px 0; border-bottom: 1px solid #e2ded2;'><b style='color: #244f3b;'>{timestamp}</b> – <span style='color: #2f7d5b;'>{emotion}</span><br/><span style='color: #5f6f68;'>{dua_title}</span></div>"
            lines.append(line)
        html_content = "".join(lines)
        self.history_label.setText(html_content)

    # --------------------------------------------------
    # Simple keyword mapping for text-based emotion input
    # --------------------------------------------------
    def _map_text_to_emotion(self, text: str) -> str:
        text = text.lower()

        mapping = {
            "angry": ["angry", "frustrated", "irritated", "annoyed", "upset", "mad", "furious"],
            "sad": ["sad", "depressed", "down", "lonely", "heartbroken", "anxious", "worried", "sorrowful"],
            "happy": ["happy", "grateful", "thankful", "excited", "joyful", "glad", "cheerful"],
            "neutral": ["ok", "fine", "normal", "calm", "alright", "good"],
            "surprise": ["surprise", "surprised", "shocked", "amazed", "astonished", "wow", "unexpected"],
        }

        for emotion, keywords in mapping.items():
            if any(word in text for word in keywords):
                return emotion

        return "neutral"

    # --------------------------------------------------
    def closeEvent(self, event):
        self.stop_camera()
        # Stop any playing audio
        self.stop_audio()
        event.accept()


# ================= RUN APP =================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = EmotionDuaApp()
    window.show()
    sys.exit(app.exec_())
