import os
import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.models import load_model

# ----- PATHS -----
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = script_dir
train_dir = os.path.join(project_root, "dataset", "train")
model_dir = os.path.join(project_root, "model")
os.makedirs(model_dir, exist_ok=True)
model_path = os.path.join(model_dir, "emotion_model.h5")

# ----- CHECK IF TRAIN DATA EXISTS -----
if os.path.exists(train_dir) and any(os.listdir(train_dir)):
    print("✅ Found training dataset. Using ImageDataGenerator...")

    # Data generator
    datagen = ImageDataGenerator(rescale=1./255)

    train_data = datagen.flow_from_directory(
        train_dir,
        target_size=(48,48),
        color_mode="grayscale",
        batch_size=32,
        class_mode="categorical"
    )

    # Build CNN
    model = Sequential([
        Conv2D(32, (3,3), activation='relu', input_shape=(48,48,1)),
        MaxPooling2D((2,2)),
        Conv2D(64, (3,3), activation='relu'),
        MaxPooling2D((2,2)),
        Flatten(),
        Dense(128, activation='relu'),
        Dense(5, activation='softmax')
    ])

    # Compile
    model.compile(optimizer=Adam(), loss='categorical_crossentropy', metrics=['accuracy'])

    # Train
    model.fit(train_data, epochs=3)

else:
    print("⚠ Training dataset not found or empty. Using dummy random data for testing...")

    # Dummy data (100 grayscale images, 5 classes)
    X_train = np.random.rand(100, 48,48,1)
    y_train = np.random.randint(0,5,100)
    y_train = np.eye(5)[y_train]

    # Build CNN
    model = Sequential([
        Conv2D(32, (3,3), activation='relu', input_shape=(48,48,1)),
        MaxPooling2D((2,2)),
        Conv2D(64, (3,3), activation='relu'),
        MaxPooling2D((2,2)),
        Flatten(),
        Dense(128, activation='relu'),
        Dense(5, activation='softmax')
    ])

    # Compile
    model.compile(optimizer=Adam(), loss='categorical_crossentropy', metrics=['accuracy'])

    # Train
    model.fit(X_train, y_train, epochs=3, batch_size=10)

# ----- SAVE MODEL -----
model.save(model_path)
print(f"✅ Model saved successfully at {model_path}")