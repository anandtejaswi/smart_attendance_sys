import sys
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QFrame,
    QLineEdit,
    QFormLayout,
    QPushButton)
from PyQt6.QtCore import Qt


class SmartAttendanceGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Smart Attendance System - Admin Dashboard")
        self.resize(1100, 700)

        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #121212;
                color: #E0E0E0;
                font-family: 'Segoe UI', sans-serif;
            }
            QFrame#Sidebar {
                background-color: #1E1E1E;
                border-left: 1px solid #333;
            }
            QLineEdit {
                background-color: #2C2C2C;
                border: 1px solid #444;
                padding: 5px;
                color: white;
            }
            QPushButton {
                background-color: #03DAC6;
                color: #000;
                font-weight: bold;
                padding: 10px;
                border-radius: 4px;
            }
        """)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QHBoxLayout(central_widget)

        # Left Column Layout
        self.left_container = QVBoxLayout()
        self.video_label = QLabel("LIVE CAMERA FEED")
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_label.setStyleSheet(
            "background-color: #000; border: 1px solid #333;")
        self.video_label.setMinimumSize(640, 480)
        self.left_container.addWidget(self.video_label)

        # Commit 20: Admin Registration Dashboard Implementation
        self.reg_frame = QFrame()
        reg_layout = QFormLayout(self.reg_frame)
        self.user_id = QLineEdit()
        self.user_name = QLineEdit()
        self.reg_btn = QPushButton("START 5-SEC VIDEO BURST")

        reg_layout.addRow("User ID:", self.user_id)
        reg_layout.addRow("Full Name:", self.user_name)
        reg_layout.addRow(self.reg_btn)

        self.left_container.addWidget(self.reg_frame)
        self.main_layout.addLayout(self.left_container, stretch=2)

        # Sidebar
        self.sidebar = QFrame()
        self.sidebar.setObjectName("Sidebar")
        self.sidebar.setFixedWidth(280)
        side_layout = QVBoxLayout(self.sidebar)
        side_header = QLabel("RECENT ACTIVITY")
        side_header.setStyleSheet(
            "font-size: 16px; font-weight: bold; color: #BB86FC;")
        self.activity_log = QLabel("Waiting for detection...")

        side_layout.addWidget(side_header)
        side_layout.addWidget(self.activity_log)
        side_layout.addStretch()
        self.main_layout.addWidget(self.sidebar)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SmartAttendanceGUI()
    window.show()
    sys.exit(app.exec())
