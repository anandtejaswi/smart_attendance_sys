import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QFrame, QLineEdit, QFormLayout, QPushButton, QStackedWidget,
    QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt6.QtCore import Qt


class SmartAttendanceGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Smart Attendance System")
        self.resize(1100, 700)

        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #F8F9FA;
                color: #212529;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QPushButton {
                background-color: #0D6EFD;
                color: white;
                font-size: 14px;
                padding: 10px 20px;
                border-radius: 5px;
                border: none;
            }
            QPushButton:hover {
                background-color: #0B5ED7;
            }
            QLineEdit {
                background-color: #FFFFFF;
                border: 1px solid #CED4DA;
                padding: 8px;
                border-radius: 4px;
                color: #212529;
            }
            QTableWidget {
                background-color: #FFFFFF;
                border: 1px solid #DEE2E6;
                gridline-color: #DEE2E6;
                font-size: 13px;
                color: #212529;
            }
            QHeaderView::section {
                background-color: #E9ECEF;
                padding: 4px;
                border: 1px solid #DEE2E6;
                font-weight: bold;
                color: #212529;
            }
            QLabel {
                color: #212529;
            }
            QFrame#Card {
                background-color: #FFFFFF;
                border-radius: 8px;
                border: 1px solid #DEE2E6;
            }
        """)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QVBoxLayout(central_widget)
        
        self.stacked_widget = QStackedWidget()
        self.main_layout.addWidget(self.stacked_widget)
        
        # Stack 0: Landing Page
        self.init_landing_page()
        # Stack 1: Attendance Tracker
        self.init_attendance_page()
        # Stack 2: Admin Dashboard
        self.init_admin_dashboard()
        
        self.stacked_widget.setCurrentIndex(0)

    def init_landing_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        title = QLabel("Smart Attendance System")
        title.setStyleSheet("font-size: 28px; font-weight: bold; margin-bottom: 30px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.landing_login_btn = QPushButton("Login as Admin")
        self.landing_login_btn.setMinimumWidth(200)
        self.landing_record_btn = QPushButton("Record Attendance Mode")
        self.landing_record_btn.setMinimumWidth(200)
        self.landing_record_btn.setStyleSheet("background-color: #198754;")
        
        layout.addWidget(title)
        layout.addWidget(self.landing_login_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addSpacing(15)
        layout.addWidget(self.landing_record_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.stacked_widget.addWidget(page)

    def init_attendance_page(self):
        page = QWidget()
        layout = QHBoxLayout(page)
        
        self.attendance_video_label = QLabel("CAMERA DISABLED")
        self.attendance_video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.attendance_video_label.setStyleSheet("background-color: #E9ECEF; border: 1px solid #CED4DA; border-radius: 8px;")
        self.attendance_video_label.setMinimumSize(640, 480)
        
        right_panel = QFrame()
        right_panel.setObjectName("Card")
        right_panel.setFixedWidth(300)
        r_layout = QVBoxLayout(right_panel)
        
        r_title = QLabel("RECENT ACTIVITY")
        r_title.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.activity_log_attendance = QLabel("Waiting for detection...")
        self.activity_log_attendance.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        self.att_back_btn = QPushButton("Return Home")
        self.att_back_btn.setStyleSheet("background-color: #6C757D;")
        
        r_layout.addWidget(r_title)
        r_layout.addWidget(self.activity_log_attendance)
        r_layout.addStretch()
        r_layout.addWidget(self.att_back_btn)
        
        layout.addWidget(self.attendance_video_label, stretch=2)
        layout.addWidget(right_panel)
        
        self.stacked_widget.addWidget(page)

    def init_admin_dashboard(self):
        page = QWidget()
        layout = QHBoxLayout(page)
        
        left_panel = QVBoxLayout()
        self.admin_video_label = QLabel("CAMERA DISABLED")
        self.admin_video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.admin_video_label.setStyleSheet("background-color: #E9ECEF; border: 1px solid #CED4DA; border-radius: 8px;")
        self.admin_video_label.setMinimumSize(400, 300)
        
        reg_frame = QFrame()
        reg_frame.setObjectName("Card")
        reg_layout = QFormLayout(reg_frame)
        self.user_id = QLineEdit()
        self.user_name = QLineEdit()
        self.reg_btn = QPushButton("Start 5-Sec Video Burst")
        self.activity_log_reg = QLabel("Ready for Registration.")
        self.activity_log_reg.setStyleSheet("color: #6C757D; margin-top: 10px;")
        
        title_label = QLabel("Register New User")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        reg_layout.addRow(title_label)
        reg_layout.addRow("User ID:", self.user_id)
        reg_layout.addRow("Full Name:", self.user_name)
        reg_layout.addRow(self.reg_btn)
        reg_layout.addRow(self.activity_log_reg)
        
        left_panel.addWidget(self.admin_video_label)
        left_panel.addWidget(reg_frame)
        
        right_panel = QVBoxLayout()
        rtitle = QLabel("Attendance Analytics")
        rtitle.setStyleSheet("font-size: 18px; font-weight: bold;")
        
        self.total_users_lbl = QLabel("Total Registered Users: 0")
        self.total_users_lbl.setStyleSheet("font-size: 14px; font-weight: bold; color: #198754;")
        
        filter_layout = QHBoxLayout()
        self.filter_btn = QPushButton("Filter Attendance Logs")
        self.filter_btn.setStyleSheet("background-color: #0DCAF0; color: #000;")
        self.clear_filter_btn = QPushButton("Clear Filters")
        self.clear_filter_btn.setStyleSheet("background-color: #6C757D;")
        filter_layout.addWidget(self.filter_btn)
        filter_layout.addWidget(self.clear_filter_btn)
        filter_layout.addStretch()
        
        self.logs_table = QTableWidget(0, 4)
        self.logs_table.setHorizontalHeaderLabels(["User ID", "Name", "Dept", "Time In"])
        self.logs_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        self.admin_back_btn = QPushButton("Logout to Home")
        self.admin_back_btn.setStyleSheet("background-color: #DC3545;")
        
        right_panel.addWidget(rtitle)
        right_panel.addWidget(self.total_users_lbl)
        right_panel.addLayout(filter_layout)
        right_panel.addWidget(self.logs_table)
        right_panel.addWidget(self.admin_back_btn, alignment=Qt.AlignmentFlag.AlignRight)
        
        layout.addLayout(left_panel, stretch=1)
        layout.addLayout(right_panel, stretch=2)
        
        self.stacked_widget.addWidget(page)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SmartAttendanceGUI()
    window.show()
    sys.exit(app.exec())
