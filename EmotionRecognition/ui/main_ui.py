import sys
import cv2
import numpy as np

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QWidget, QFrame
)
from PyQt5.QtGui import QFont, QImage, QPixmap
from PyQt5.QtCore import Qt, QTimer

from tensorflow.keras.models import load_model

class EmotionDuaApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Emotion-Based Dua Recommendation System")
        self.setGeometry(100, 100, 1100, 600)

        # ================= LOAD MODEL =================
        # Use the converted model which is compatible with current TF
        self.model = load_model(
            r"C:\Users\Mahek\PycharmProjects\PythonProject1\EmotionRecognition\model\emotion_model.h5",
            compile=False
        )
        print("✅ Emotion model loaded successfully")

        self.classes = ['angry', 'happy', 'neutral', 'sad', 'surprise']

        # ================= FACE DETECTOR =================
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )

        # ================= CAMERA =================
        self.cap = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)

        # ================= UI =================
        self.init_ui()

    # --------------------------------------------------
    def init_ui(self):
        main_widget = QWidget()
        main_layout = QHBoxLayout()

        # -------- CAMERA PANEL --------
        self.camera_label = QLabel("Camera Off")
        self.camera_label.setFixedSize(640, 480)
        self.camera_label.setAlignment(Qt.AlignCenter)
        self.camera_label.setStyleSheet(
            "background-color: black; color: white; border: 2px solid green;"
        )

        # -------- DUA PANEL --------
        right_panel = QFrame()
        right_layout = QVBoxLayout()

        self.emotion_label = QLabel("Emotion: ---")
        self.emotion_label.setFont(QFont("Arial", 16, QFont.Bold))

        self.dua_label = QLabel("Dua will appear here")
        self.dua_label.setFont(QFont("Arial", 14))
        self.dua_label.setWordWrap(True)

        right_layout.addWidget(self.emotion_label)
        right_layout.addSpacing(20)
        right_layout.addWidget(self.dua_label)
        right_layout.addStretch()

        right_panel.setLayout(right_layout)

        # -------- BUTTONS --------
        self.start_btn = QPushButton("▶ Start")
        self.pause_btn = QPushButton("⏸ Pause")
        self.exit_btn = QPushButton("❌ Exit")

        self.start_btn.clicked.connect(self.start_camera)
        self.pause_btn.clicked.connect(self.stop_camera)
        self.exit_btn.clicked.connect(self.close)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.start_btn)
        btn_layout.addWidget(self.pause_btn)
        btn_layout.addWidget(self.exit_btn)

        left_layout = QVBoxLayout()
        left_layout.addWidget(self.camera_label)
        left_layout.addLayout(btn_layout)

        main_layout.addLayout(left_layout)
        main_layout.addWidget(right_panel)

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

            self.emotion_label.setText(f"Emotion: {emotion.upper()}")
            self.dua_label.setText(self.get_dua(emotion))

            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(frame, emotion, (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        bytes_per_line = ch * w
        qt_img = QImage(rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
        self.camera_label.setPixmap(QPixmap.fromImage(qt_img))

    # --------------------------------------------------
    def get_dua(self, emotion):
        duas = {
            "angry": "اللَّهُمَّ اغْفِرْ لِي وَأَذْهِبْ غَيْظَ قَلْبِي",
            "sad": "اللَّهُمَّ إِنِّي أَعُوذُ بِكَ مِنَ الْهَمِّ وَالْحَزَنِ",
            "happy": "الْحَمْدُ لِلَّهِ الَّذِي بِنِعْمَتِهِ تَتِمُّ الصَّالِحَاتُ",
            "neutral": "رَبِّ زِدْنِي عِلْمًا",
            "surprise": "سُبْحَانَ اللَّهِ وَبِحَمْدِهِ"
        }
        return duas.get(emotion, "")

    # --------------------------------------------------
    def closeEvent(self, event):
        self.stop_camera()
        event.accept()


# ================= RUN APP =================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = EmotionDuaApp()
    window.show()
    sys.exit(app.exec_())
