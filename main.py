import sys
import cv2
import warnings

from PyQt6.QtWidgets import QApplication, QInputDialog, QLineEdit, QMessageBox, QTableWidgetItem
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QImage, QPixmap

from src.gui import SmartAttendanceGUI
from src.hardware.camera import VideoCapture
from src.recognition import RecognitionEngine
from src.data_manager import DataManager

warnings.filterwarnings("ignore")

class SmartAttendanceApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.gui = SmartAttendanceGUI()

        self.data_manager = DataManager()
        self.data_manager.db_manager.create_tables()
        self.known_encodings = self.data_manager.retrieve_encodings()

        self.camera = VideoCapture(0)
        self.engine = RecognitionEngine()

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)

        self.is_registering = False
        self.registration_encodings = []
        self.new_user_id = ""
        self.new_user_name = ""
        self.new_user_dept = ""
        
        self.current_filter_type = None
        self.current_filter_value = None

        # Connect GUI signals
        self.gui.landing_login_btn.clicked.connect(self.prompt_admin_login)
        self.gui.landing_record_btn.clicked.connect(self.start_attendance_tracking)
        self.gui.att_back_btn.clicked.connect(self.go_home)
        self.gui.admin_back_btn.clicked.connect(self.go_home)
        
        self.gui.reg_btn.clicked.connect(self.start_registration)
        self.gui.filter_btn.clicked.connect(self.prompt_filter)
        self.gui.clear_filter_btn.clicked.connect(self.clear_filter)
        self.gui.show_users_btn.clicked.connect(self.show_all_users_dialog)
        self.gui.analytics_btn.clicked.connect(self.show_analytics_dialog)
        self.gui.profile_btn.clicked.connect(self.show_profile_dialog)
        
        self.gui.activity_log_attendance.setText("System Initializing: Camera Booting...")

    def get_admin_password(self):
        import os
        pwd_file = ".admin_auth"
        if os.path.exists(pwd_file):
            with open(pwd_file, "r") as f:
                return f.read().strip()
        return "admin"
        
    def set_admin_password(self, new_pwd):
        with open(".admin_auth", "w") as f:
            f.write(new_pwd)

    def prompt_admin_login(self):
        user_id, ok1 = QInputDialog.getText(
            self.gui, "Admin Login", "Enter Admin ID:")
        if ok1 and user_id == "admin":
            password, ok2 = QInputDialog.getText(
                self.gui, "Admin Login", "Enter Admin Password:", QLineEdit.EchoMode.Password)
            correct_pwd = self.get_admin_password()
            if ok2 and password == correct_pwd:
                self.start_admin_dashboard()
            else:
                QMessageBox.warning(self.gui, "Login Failed", "Invalid Admin Password.")
        elif ok1:
            QMessageBox.warning(self.gui, "Login Failed", "Invalid Admin ID.")

    def start_admin_dashboard(self):
        self.gui.stacked_widget.setCurrentIndex(2) # Admin
        self.populate_analytics_table()

    def start_attendance_tracking(self):
        self.gui.stacked_widget.setCurrentIndex(1) # Attendance

    def go_home(self):
        self.gui.stacked_widget.setCurrentIndex(0) # Landing

    def populate_analytics_table(self):
        logs = self.data_manager.get_filtered_logs(
            limit=50, 
            filter_type=self.current_filter_type, 
            filter_value=self.current_filter_value
        )
        total_users = self.data_manager.get_total_users()
        self.gui.total_users_lbl.setText(f"Total Registered Users: {total_users}")
        
        self.gui.logs_table.setRowCount(0)
        for i, row in enumerate(logs):
            self.gui.logs_table.insertRow(i)
            self.gui.logs_table.setItem(i, 0, QTableWidgetItem(str(row["user_id"])))
            self.gui.logs_table.setItem(i, 1, QTableWidgetItem(str(row["name"])))
            self.gui.logs_table.setItem(i, 2, QTableWidgetItem(str(row["dept"])))
            self.gui.logs_table.setItem(i, 3, QTableWidgetItem(str(row["time_in"])))

    def clear_filter(self):
        self.current_filter_type = None
        self.current_filter_value = None
        self.populate_analytics_table()

    def prompt_filter(self):
        filter_type, ok = QInputDialog.getItem(
            self.gui, 
            "Filter Attendance Logs", 
            "Filter by:", 
            ["User ID", "Date"], 
            0, 
            False
        )
        if ok and filter_type:
            if filter_type == "User ID":
                val, ok_val = QInputDialog.getText(self.gui, "Filter Logs", "Enter exact User ID to search:")
                if ok_val and val.strip():
                    self.current_filter_type = "User ID"
                    self.current_filter_value = val.strip()
                    self.populate_analytics_table()
            elif filter_type == "Date":
                val, ok_val = QInputDialog.getText(self.gui, "Filter Logs", "Enter Date (YYYY-MM-DD):")
                if ok_val and val.strip():
                    import re
                    if re.match(r"^\d{4}-\d{2}-\d{2}$", val.strip()):
                        self.current_filter_type = "Date"
                        self.current_filter_value = val.strip()
                        self.populate_analytics_table()
                    else:
                        QMessageBox.warning(self.gui, "Invalid Format", "Please use strict YYYY-MM-DD format.")

    def show_all_users_dialog(self):
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QTableWidget, QHeaderView
        dialog = QDialog(self.gui)
        dialog.setWindowTitle("All Registered Users")
        dialog.resize(600, 400)
        
        layout = QVBoxLayout(dialog)
        users = self.data_manager.get_all_users()
        
        table = QTableWidget(len(users), 4)
        table.setHorizontalHeaderLabels(["User ID", "Name", "Dept", "Reg Date"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        for i, user in enumerate(users):
            table.setItem(i, 0, QTableWidgetItem(str(user["user_id"])))
            table.setItem(i, 1, QTableWidgetItem(str(user["name"])))
            table.setItem(i, 2, QTableWidgetItem(str(user["dept"])))
            table.setItem(i, 3, QTableWidgetItem(str(user["reg_date"])))
            
        layout.addWidget(table)
        dialog.exec()

    def show_analytics_dialog(self):
        user_id, ok = QInputDialog.getText(self.gui, "User Analytics", "Enter exact User ID:")
        if not ok or not user_id.strip():
            return
            
        user_id = user_id.strip()
        calendar_logs = self.data_manager.get_user_calendar_logs(user_id)
        
        if not calendar_logs:
            QMessageBox.information(self.gui, "No Data", f"No attendance logs found for '{user_id}'.")
            return
            
        from PyQt6.QtWidgets import QDialog, QHBoxLayout, QVBoxLayout, QLabel, QCalendarWidget, QListWidget
        from PyQt6.QtGui import QTextCharFormat, QColor, QFont
        from PyQt6.QtCore import QDate
        
        dialog = QDialog(self.gui)
        dialog.setWindowTitle(f"Analytics Graph: {user_id}")
        dialog.resize(800, 500)
        
        layout = QHBoxLayout(dialog)
        
        distinct_days = len(calendar_logs.keys())
        total_seconds = 0
        from datetime import datetime
        
        for date_key, times in calendar_logs.items():
            first_time = times[0]
            try:
                t_obj = datetime.strptime(first_time, "%H:%M:%S")
                seconds = t_obj.hour * 3600 + t_obj.minute * 60 + t_obj.second
                total_seconds += seconds
            except:
                pass
                
        avg_seconds = total_seconds / distinct_days if distinct_days > 0 else 0
        avg_time = "N/A"
        if avg_seconds > 0:
            h = int(avg_seconds // 3600)
            m = int((avg_seconds % 3600) // 60)
            avg_time_obj = datetime.strptime(f"{h}:{m}:00", "%H:%M:%S")
            avg_time = avg_time_obj.strftime("%I:%M %p")
            
        left_panel = QVBoxLayout()
        stats_lbl = QLabel(f"<b>User:</b> {user_id}<br><br>"
                           f"<b>Total Distinct Days Present:</b> {distinct_days}<br>"
                           f"<b>Average Daily Arrival:</b> {avg_time}")
        stats_lbl.setStyleSheet("font-size: 16px;")
        
        cal = QCalendarWidget()
        cal.setGridVisible(True)
        
        fmt = QTextCharFormat()
        fmt.setForeground(QColor("white"))
        fmt.setBackground(QColor("#198754"))
        fmt.setFontWeight(QFont.Weight.Bold)
        
        for date_str in calendar_logs.keys():
            try:
                qdate = QDate.fromString(date_str, "yyyy-MM-dd")
                cal.setDateTextFormat(qdate, fmt)
            except:
                pass
                
        left_panel.addWidget(stats_lbl)
        left_panel.addWidget(cal)
        
        right_panel = QVBoxLayout()
        right_panel.addWidget(QLabel("<b>Log Times on Selected Date:</b>"))
        list_widget = QListWidget()
        right_panel.addWidget(list_widget)
        
        def on_date_clicked(qdate):
            date_key = qdate.toString("yyyy-MM-dd")
            list_widget.clear()
            if date_key in calendar_logs:
                for t in calendar_logs[date_key]:
                    list_widget.addItem(t)
            else:
                list_widget.addItem("No logs found.")
                
        cal.clicked.connect(on_date_clicked)
        on_date_clicked(cal.selectedDate())
        
        layout.addLayout(left_panel, stretch=2)
        layout.addLayout(right_panel, stretch=1)
        
        dialog.exec()

    def show_profile_dialog(self):
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton
        dialog = QDialog(self.gui)
        dialog.setWindowTitle("Admin Profile")
        dialog.resize(300, 200)
        
        layout = QVBoxLayout(dialog)
        layout.addWidget(QLabel("<b>Admin ID:</b> admin"))
        
        new_pwd_input = QLineEdit()
        new_pwd_input.setEchoMode(QLineEdit.EchoMode.Password)
        new_pwd_input.setPlaceholderText("Enter new password")
        
        confirm_pwd_input = QLineEdit()
        confirm_pwd_input.setEchoMode(QLineEdit.EchoMode.Password)
        confirm_pwd_input.setPlaceholderText("Confirm new password")
        
        save_btn = QPushButton("Change Password")
        save_btn.setStyleSheet("background-color: #28A745; color: white;")
        
        def save_pwd():
            pwd1 = new_pwd_input.text()
            pwd2 = confirm_pwd_input.text()
            if not pwd1:
                QMessageBox.warning(dialog, "Error", "Password cannot be empty!")
                return
            if pwd1 != pwd2:
                QMessageBox.warning(dialog, "Error", "Passwords do not match!")
                return
            self.set_admin_password(pwd1)
            QMessageBox.information(dialog, "Success", "Admin password successfully updated!")
            dialog.accept()
            
        save_btn.clicked.connect(save_pwd)
        
        layout.addWidget(QLabel("Change Password:"))
        layout.addWidget(new_pwd_input)
        layout.addWidget(confirm_pwd_input)
        layout.addWidget(save_btn)
        
        dialog.exec()

    def start_registration(self):
        user_id = self.gui.user_id.text().strip()
        user_name = self.gui.user_name.text().strip()
        user_dept = self.gui.user_dept.text().strip()
        
        if not user_id or not user_name or not user_dept:
            self.gui.activity_log_reg.setText("ERROR: ID, Name, Dept required!")
            return
            
        if user_id in self.known_encodings:
            self.gui.activity_log_reg.setText("ERROR: User ID already exists!")
            return

        self.is_registering = True
        self.registration_encodings = []
        self.new_user_id = user_id
        self.new_user_name = user_name
        self.new_user_dept = user_dept
        self.gui.activity_log_reg.setText("RECORDING: Please look at camera...")

    def update_frame(self):
        frame = self.camera.get_downsampled_frame()
        if frame is None:
            return

        bboxes = self.engine.detect_face(frame)

        for (x, y, w, h) in bboxes:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        if len(bboxes) > 0:
            current_encoding = self.engine.generate_encoding(frame)
            if current_encoding is not None:
                if self.is_registering and self.gui.stacked_widget.currentIndex() == 2:
                    self.registration_encodings.append(current_encoding)
                    self.gui.activity_log_reg.setText(f"RECORDING: {len(self.registration_encodings)}/10 frames...")
                    
                    if len(self.registration_encodings) >= 10:
                        import numpy as np
                        from src.security import AuthManager
                        
                        avg_encoding = np.mean(self.registration_encodings, axis=0)
                        auth_manager = AuthManager()
                        hashed_pwd = auth_manager.hash_password("admin")
                        
                        success = self.data_manager.insert_user(
                            user_id=self.new_user_id,
                            name=self.new_user_name,
                            dept=self.new_user_dept,
                            encoding_array=avg_encoding,
                            pwd_hash=hashed_pwd,
                            role="User"
                        )
                        
                        if success:
                            self.known_encodings[self.new_user_id] = avg_encoding
                            self.gui.activity_log_reg.setText(f"SUCCESS: Enrolled {self.new_user_name}")
                            self.gui.user_id.clear()
                            self.gui.user_name.clear()
                            self.gui.user_dept.clear()
                            self.populate_analytics_table()
                        else:
                            self.gui.activity_log_reg.setText("ERROR: DB Insertion Failed")
                            
                        self.is_registering = False
                        self.registration_encodings = []
                elif self.gui.stacked_widget.currentIndex() == 1:
                    matched_uid = None

                    for uid, saved_enc in self.known_encodings.items():
                        dist, is_match = self.engine.compare_encoding(
                            current_encoding, saved_enc)
                        if is_match:
                            matched_uid = uid
                            break

                    if matched_uid:
                        if self.engine.check_stability(matched_uid):
                            success = self.data_manager.log_attendance(matched_uid)
                            if success:
                                import datetime
                                current_time = datetime.datetime.now().strftime("%I:%M %p")
                                QMessageBox.information(
                                    self.gui,
                                    "Attendance Logged",
                                    f"Your Attendance has been Logged at {current_time}\nUser ID: {matched_uid}"
                                )
                                self.gui.activity_log_attendance.setText("Waiting for detection...")
                                self.engine.check_stability(None)
                                self.go_home()
                    else:
                        self.engine.check_stability(None)
                        self.gui.activity_log_attendance.setText("UNKNOWN FACE DETECTED")
        else:
            self.engine.check_stability(None)
            if self.gui.stacked_widget.currentIndex() == 1:
                self.gui.activity_log_attendance.setText("Waiting for detection...")

        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w

        q_img = QImage(
            rgb_image.data,
            w,
            h,
            bytes_per_line,
            QImage.Format.Format_RGB888)

        pixmap = QPixmap.fromImage(q_img)

        # Route feed depending on which page is active
        if self.gui.stacked_widget.currentIndex() == 1:
            self.gui.attendance_video_label.setPixmap(pixmap)
        elif self.gui.stacked_widget.currentIndex() == 2:
            self.gui.admin_video_label.setPixmap(pixmap)

    def run(self):
        self.gui.show()
        exit_code = self.app.exec()
        self.camera.release()
        sys.exit(exit_code)

if __name__ == "__main__":
    app_instance = SmartAttendanceApp()
    app_instance.run()
