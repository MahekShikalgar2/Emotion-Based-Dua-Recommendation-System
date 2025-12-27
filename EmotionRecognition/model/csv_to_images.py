import csv
import os
import numpy as np
import cv2

# Emotion mapping from FER2013
emotion_map = {
    0: 'angry',
    3: 'happy',
    4: 'sad',
    6: 'neutral',
    5: 'surprise'
}

base_dir = "../dataset/train"
os.makedirs(base_dir, exist_ok=True)

with open('../fer2013.csv') as file:
    reader = csv.reader(file)
    next(reader)  # skip header

    for i, row in enumerate(reader):
        emotion = int(row[0])

        if emotion in emotion_map:
            pixels = np.array(row[1].split(), dtype='uint8')
            image = pixels.reshape(48, 48)

            folder = os.path.join(base_dir, emotion_map[emotion])
            os.makedirs(folder, exist_ok=True)

            cv2.imwrite(f"{folder}/{i}.jpg", image)

print("✅ CSV successfully converted to images!")
