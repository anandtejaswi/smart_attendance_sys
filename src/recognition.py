import cv2
import numpy as np
import dlib
import face_recognition


class RecognitionEngine:
    """
    Core engine for facial recognition tasks including face detection,
    encoding generation, identity matching, and liveness (blink) detection.
    """

    def __init__(self):
        # Dlib HOG algorithm for face detection
        self.face_detector = dlib.get_frontal_face_detector()
        self.last_user = None
        self.frame_count = 0

    def detect_face(self, frame):
        """
        Detects faces in a given frame using Dlib's HOG face detector.
        Returns a list of bounding boxes (x, y, w, h) for each detected face.
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
""" 
converts to grayscale for faster processing 
dlib’s HOG-based detector to find face locations
"""

        faces = self.face_detector(gray, 1)

        bboxes = []
        for face in faces:
            x = face.left()
            y = face.top()
            w = face.width()
            h = face.height()
            bboxes.append((x, y, w, h))

        return bboxes

    def generate_encoding(self, frame):
        """
        Extracts the 128-dimensional facial encoding from the frame 
        using the face_recognition library.
        """
        # Convert OpenCV BGR format to RGB for face_recognition
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Extract the 128-dimensional floating-point encoding
        encodings = face_recognition.face_encodings(rgb_frame)

        # Commit 11 constraint: forcefully purge raw image array from memory
        del frame
        del rgb_frame

        if len(encodings) > 0:
            return encodings[0]
        return None

    def compare_encoding(self, enc1, enc2):
        """
        Compares two facial encodings using Euclidean distance.
        Returns the distance and a boolean indicating if it's a match 
        based on a strict threshold.
        """
        distance = np.linalg.norm(enc1 - enc2)
        
        # Enforcing matching threshold
        is_match = distance <= 0.55
        """ 
        for strict matching to decide if 2 faces match
        """
        return distance, is_match

    def check_stability(self, current_user):
        """
        Checks if the same user has been detected consecutively for 
        a set number of frames to ensure stability before logging attendance.
        """
        if self.last_user == current_user:
            self.frame_count += 1
        else:
            self.last_user = current_user
            self.frame_count = 1

        if self.frame_count >= 3:
            self.frame_count = 0
            return True

        return False

    def calculate_ear(self, eye):
        """
        Calculates the Eye Aspect Ratio (EAR)used to detect blinking given eye landmarks.
        Used to detect if the eye is open or closed.
        """
        import math
        # Calculate Euclidean distances (to measure similarity between faces) between vertical eye landmarks
        a = math.dist(eye[1], eye[5])
        b = math.dist(eye[2], eye[4])
        # Calculate Euclidean distance between horizontal eye landmarks
        c = math.dist(eye[0], eye[3])
        
        if c == 0:
            return 0.0
            
        ear = (a + b) / (2.0 * c)
        return ear

    def detect_blink(self, frame):
        """
        Analyzes facial landmarks to detect a blink event.
        A blink is considered a liveness check to prevent spoofing with photos.
        """
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        landmarks_list = face_recognition.face_landmarks(rgb_frame)
        
        if not landmarks_list:
            return False

        for face_landmark in landmarks_list:
            if 'left_eye' in face_landmark and 'right_eye' in face_landmark:
                left_ear = self.calculate_ear(face_landmark['left_eye'])
                right_ear = self.calculate_ear(face_landmark['right_eye'])
                
                avg_ear = (left_ear + right_ear) / 2.0
                
                # A blink traditionally triggers below 0.22 depending on angle
                if avg_ear < 0.22:
                    return True
                    """
                    means blink detected
                    """
        return False
