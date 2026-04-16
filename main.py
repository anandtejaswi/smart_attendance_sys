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
        
        self.gui.activity_log_attendance.setText("System Initializing: Camera Booting...")

    def prompt_admin_login(self):
        user_id, ok1 = QInputDialog.getText(self.gui, "Admin Login", "Enter User ID:")
        if ok1 and user_id == "admin":
            password, ok2 = QInputDialog.getText(self.gui, "Admin Login", "Enter Password:", QLineEdit.EchoMode.Password)
            if ok2 and password == "admin":
                self.start_admin_dashboard()
            else:
                QMessageBox.warning(self.gui, "Login Failed", "Incorrect password.")
        elif ok1:
            QMessageBox.warning(self.gui, "Login Failed", "Incorrect User ID.")

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
        
        table = QTableWidget(len(users), 5)
        table.setHorizontalHeaderLabels(["User ID", "Name", "Dept", "Reg Date", "Role"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        for i, user in enumerate(users):
            table.setItem(i, 0, QTableWidgetItem(str(user["user_id"])))
            table.setItem(i, 1, QTableWidgetItem(str(user["name"])))
            table.setItem(i, 2, QTableWidgetItem(str(user["dept"])))
            table.setItem(i, 3, QTableWidgetItem(str(user["reg_date"])))
            table.setItem(i, 4, QTableWidgetItem(str(user["role"])))
            
        layout.addWidget(table)
        dialog.exec()

    def start_registration(self):
        user_id = self.gui.user_id.text().strip()
        user_name = self.gui.user_name.text().strip()
        
        if not user_id or not user_name:
            self.gui.activity_log_reg.setText("ERROR: ID & Name required!")
            return
            
        if user_id in self.known_encodings:
            self.gui.activity_log_reg.setText("ERROR: User ID already exists!")
            return

        self.is_registering = True
        self.registration_encodings = []
        self.new_user_id = user_id
        self.new_user_name = user_name
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
                            dept="General",
                            encoding_array=avg_encoding,
                            pwd_hash=hashed_pwd,
                            role="User"
                        )
                        
                        if success:
                            self.known_encodings[self.new_user_id] = avg_encoding
                            self.gui.activity_log_reg.setText(f"SUCCESS: Enrolled {self.new_user_name}")
                            self.gui.user_id.clear()
                            self.gui.user_name.clear()
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
                                    f"Your Attendance has been Logged at {current_time}"
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
