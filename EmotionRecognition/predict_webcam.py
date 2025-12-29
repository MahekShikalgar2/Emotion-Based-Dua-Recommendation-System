import cv2
import numpy as np
from tensorflow.keras.models import load_model

# Load the trained model
import os
script_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(script_dir, 'model', 'emotion_model.h5')
model = load_model(model_path)

# Emotion classes
classes = ['angry', 'happy', 'neutral', 'sad', 'surprise']

# Initialize webcam
cap = cv2.VideoCapture(0)
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

print("Webcam running... Press 'q' to quit.")

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Adjusted scaleFactor and minNeighbors for better detection
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=4)

    for (x, y, w, h) in faces:
        roi_gray = gray[y:y + h, x:x + w]
        roi_gray = cv2.resize(roi_gray, (48, 48))
        roi = roi_gray.reshape(1, 48, 48, 1) / 255.0

        # Predict emotion
        prediction = model.predict(roi)
        predicted_class = classes[np.argmax(prediction)]
        confidence = np.max(prediction) * 100  # Convert to percentage

        # Draw rectangle and label
        label = f"{predicted_class} ({confidence:.1f}%)"
        label_y = y - 10 if y - 10 > 10 else y + 20
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
        cv2.putText(frame, label, (x, label_y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

    # Display the frame
    cv2.imshow('Emotion Recognition', frame)

    # Exit on pressing 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("Exiting...")
        break

# Release resources
cap.release()
cv2.destroyAllWindows()
