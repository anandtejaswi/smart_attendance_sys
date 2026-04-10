import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QFrame
from PyQt6.QtCore import Qt

class SmartAttendanceGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Smart Attendance System - Admin Dashboard")
        self.resize(1100, 700)
        
        # Dark Theme Stylesheet
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #121212;
                color: #E0E0E0;
                font-family: 'Segoe UI', sans-serif;
            }
        """)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QHBoxLayout(central_widget)

        # Left Container for Video
        self.left_container = QVBoxLayout()
        self.video_label = QLabel("LIVE CAMERA FEED")
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_label.setStyleSheet("background-color: #000; border: 1px solid #333;")
        self.video_label.setMinimumSize(640, 480)
        self.left_container.addWidget(self.video_label)
        self.main_layout.addLayout(self.left_container, stretch=2)

        # Commit 19: Recent Activity Sidebar Implementation
        self.sidebar = QFrame()
        self.sidebar.setFixedWidth(280)
        self.sidebar.setStyleSheet("background-color: #1E1E1E; border-left: 1px solid #333;")
        side_layout = QVBoxLayout(self.sidebar)
        
        header = QLabel("RECENT ACTIVITY")
        header.setStyleSheet("font-size: 16px; font-weight: bold; color: #BB86FC; margin-bottom: 10px;")
        
        self.activity_log = QLabel("Waiting for detection...")
        self.activity_log.setWordWrap(True)
        self.activity_log.setStyleSheet("color: #03DAC6;")
        
        side_layout.addWidget(header)
        side_layout.addWidget(self.activity_log)
        side_layout.addStretch()
        
        self.main_layout.addWidget(self.sidebar)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SmartAttendanceGUI()
    window.show()
    sys.exit(app.exec())