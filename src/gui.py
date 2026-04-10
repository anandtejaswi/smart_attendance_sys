import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout
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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SmartAttendanceGUI()
    window.show()
    sys.exit(app.exec())