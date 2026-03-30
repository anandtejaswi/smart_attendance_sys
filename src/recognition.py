import cv2
import numpy as np

class RecognitionEngine:

    def __init__(self):
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )

    def detect_face(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.3,
            minNeighbors=5
        )

        return faces

    def generate_encoding(self, frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    resized = cv2.resize(gray, (16, 8))  # 128 values
    encoding = resized.flatten() / 255.0
    return encoding

    def compare_encoding(self, enc1, enc2):
    distance = np.linalg.norm(enc1 - enc2)
    return distance, distance < 0.6