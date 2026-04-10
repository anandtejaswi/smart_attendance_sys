import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt

class SmartAttendanceGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Smart Attendance System - Admin Dashboard")
        self.resize(1100, 700)
        self.setStyleSheet("QMainWindow, QWidget { background-color: #121212; color: #E0E0E0; }")

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QHBoxLayout(central_widget)
        self.left_container = QVBoxLayout()

        # Commit 18: Video Viewport
        self.video_label = QLabel("LIVE CAMERA FEED")
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_label.setStyleSheet("background-color: #000; border: 1px solid #333;")
        self.video_label.setMinimumSize(640, 480)
        
        self.left_container.addWidget(self.video_label)
        self.main_layout.addLayout(self.left_container, stretch=2)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SmartAttendanceGUI()
    window.show()
    sys.exit(app.exec())