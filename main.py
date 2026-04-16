import sys
import cv2
import warnings

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QImage, QPixmap

from src.gui import SmartAttendanceGUI
from src.hardware.camera import VideoCapture
from src.recognition import RecognitionEngine
from src.data_manager import DataManager

# Suppress minor warnings for production
warnings.filterwarnings("ignore")


class SmartAttendanceApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.gui = SmartAttendanceGUI()

        self.data_manager = DataManager()
        self.data_manager.db_manager.create_tables()
        self.known_encodings = self.data_manager.retrieve_encodings()

        # Initialize hardware and analysis layers
        self.camera = VideoCapture(0)
        self.engine = RecognitionEngine()

        # Link GUI to system updates roughly ~30 FPS
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)

        self.gui.activity_log.setText("System Initializing: Camera Booting...")

    def update_frame(self):
        frame = self.camera.get_downsampled_frame()
        if frame is None:
            return

        # Perform face detection
        bboxes = self.engine.detect_face(frame)

        # Display bounding boxes with green color (0, 255, 0)
        for (x, y, w, h) in bboxes:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        if len(bboxes) > 0:
            current_encoding = self.engine.generate_encoding(frame)
            if current_encoding is not None:
                matched_uid = None

                # Check against known encodings
                for uid, saved_enc in self.known_encodings.items():
                    dist, is_match = self.engine.compare_encoding(
                        current_encoding, saved_enc)
                    if is_match:
                        matched_uid = uid
                        break

                if matched_uid:
                    # Stabilize to avoid false positives in blink-frames
                    if self.engine.check_stability(matched_uid):
                        success = self.data_manager.log_attendance(matched_uid)
                        if success:
                            self.gui.activity_log.setText(
                                f"SUCCESS: Logged {matched_uid}")
                else:
                    self.engine.check_stability(None)
                    self.gui.activity_log.setText("UNKNOWN FACE DETECTED")
        else:
            self.engine.check_stability(None)
            self.gui.activity_log.setText("Waiting for detection...")

        # PyQT uses RGB format while OpenCV feeds raw BGR
        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w

        q_img = QImage(
            rgb_image.data,
            w,
            h,
            bytes_per_line,
            QImage.Format.Format_RGB888)
        self.gui.video_label.setPixmap(QPixmap.fromImage(q_img))

    def run(self):
        self.gui.show()
        # Execution loop
        exit_code = self.app.exec()

        # Safe breakdown for hardware closing
        self.camera.release()
        sys.exit(exit_code)


if __name__ == "__main__":
    app_instance = SmartAttendanceApp()
    app_instance.run()
