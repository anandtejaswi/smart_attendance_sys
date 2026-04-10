import sqlite3
import psycopg2
import numpy as np
import pandas as pd
from psycopg2 import OperationalError
from .database import DBConnectionManager

class DataManager:
    """
    Handles CRUD operations and business logic required to bridge 
    the Application Layer with the Data Layer.
    """
    def __init__(self):
        self.db_manager = DBConnectionManager()

    def insert_user(self, user_id, name, dept, encoding_array, pwd_hash, role="User"):
        """
        Inserts a new user into the Users table. 
        Converts the 128-d numpy encoding array into bytes for DB storage.
        """
        conn = None
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            # Serialize the numpy array to bytes
            encoding_bytes = encoding_array.tobytes()
            
            # Parameterized queries to prevent SQL injection (Phase 7 prerequisite)
            if self.db_manager.db_type == "sqlite":
                query = "INSERT INTO Users (user_id, name, dept, encoding, pwd_hash, role) VALUES (?, ?, ?, ?, ?, ?)"
            else:
                query = "INSERT INTO Users (user_id, name, dept, encoding, pwd_hash, role) VALUES (%s, %s, %s, %s, %s, %s)"

            cursor.execute(query, (user_id, name, dept, encoding_bytes, pwd_hash, role))
            conn.commit()
            return True
        except (sqlite3.Error, OperationalError) as e:
            print(f"Error inserting user: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn:
                cursor.close()
                self.db_manager.close_connection(conn)

    def retrieve_encodings(self):
        """
        Retrieves all users and their facial encodings.
        Returns a dictionary mapping user_id -> numpy encoding array (128-d float).
        """
        conn = None
        user_encodings = {}
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            query = "SELECT user_id, encoding FROM Users"
            cursor.execute(query)
            
            rows = cursor.fetchall()
            for row in rows:
                if self.db_manager.db_type == 'sqlite':
                    user_id = row['user_id']
                    encoding_bytes = row['encoding']
                else:
                    user_id = row[0]
                    encoding_bytes = bytes(row[1]) # psycopg2 returns memoryview for BYTEA
                
                # Deserialize back into a numpy float64 array
                encoding_array = np.frombuffer(encoding_bytes, dtype=np.float64)
                user_encodings[user_id] = encoding_array
                
        except (sqlite3.Error, OperationalError) as e:
            print(f"Error retrieving encodings: {e}")
        finally:
            if conn:
                cursor.close()
                self.db_manager.close_connection(conn)
        
        return user_encodings

    def get_all_users(self):
        """Fetches basic user info (excluding encodings and hashes) for management UI."""
        conn = None
        users = []
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            query = "SELECT user_id, name, dept, reg_date, role FROM Users"
            cursor.execute(query)
            
            rows = cursor.fetchall()
            for row in rows:
                if self.db_manager.db_type == 'sqlite':
                    users.append(dict(row))
                else:
                    users.append({
                        "user_id": row[0],
                        "name": row[1],
                        "dept": row[2],
                        "reg_date": row[3],
                        "role": row[4]
                    })
                    
        except (sqlite3.Error, OperationalError) as e:
            print(f"Error retrieving user records: {e}")
        finally:
            if conn:
                cursor.close()
                self.db_manager.close_connection(conn)
                
        return users

    def log_attendance(self, user_id, confidence=1.0):
        """
        Commit 15: Automatically dispatch insertion query to Attendance_Logs.
        Should be called by the application loop once the 3-frame stability threshold is met.
        """
        conn = None
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            if self.db_manager.db_type == "sqlite":
                query = "INSERT INTO Attendance_Logs (user_id, confidence) VALUES (?, ?)"
            else:
                query = "INSERT INTO Attendance_Logs (user_id, confidence) VALUES (%s, %s)"
                
            cursor.execute(query, (user_id, confidence))
            conn.commit()
            return True
        except (sqlite3.Error, OperationalError) as e:
            print(f"Error logging attendance: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn:
                cursor.close()
                self.db_manager.close_connection(conn)

    def export_attendance_analytics(self, expected_sessions=1, export_dir="."):
        """
        Commit 16: Integrate Pandas for attendance analytics and data export.
        Filters logs, identifies sub-75% attendance metrics against expected_sessions,
        and provides one-click CSV and XLSX export conforming to ISO 8601 timestamps.
        """
        conn = None
        try:
            conn = self.db_manager.get_connection()
            
            # Extract main attendance string logic matching users with their timestamps
            query = '''
                SELECT 
                    a.log_id,
                    a.user_id,
                    u.name,
                    u.dept,
                    a.time_in,
                    a.confidence
                FROM Attendance_Logs a
                JOIN Users u ON a.user_id = u.user_id
            '''
            
            # Leverage Pandas to directly fetch and parse SQL table
            df = pd.read_sql_query(query, conn)
            
            if df.empty:
                print("No attendance records found.")
                return False
                
            # Commit 16 constraint: Ensure ISO 8601 formatting for exports
            df['time_in'] = pd.to_datetime(df['time_in'])
            df['iso_time_in'] = df['time_in'].dt.strftime('%Y-%m-%dT%H:%M:%S')
            
            # Analytics: identifying sub-75% attendance metrics
            # Group by user metadata and count frequency of attendance
            analytics_df = df.groupby(['user_id', 'name', 'dept']).size().reset_index(name='sessions_attended')
            
            # Avoid division by zero
            safe_sessions = expected_sessions if expected_sessions > 0 else 1
            analytics_df['attendance_percent'] = (analytics_df['sessions_attended'] / safe_sessions) * 100
            analytics_df['sub_75_flag'] = analytics_df['attendance_percent'] < 75.0
            
            # Export Raw Logs
            raw_csv = f"{export_dir}/attendance_logs.csv"
            raw_xlsx = f"{export_dir}/attendance_logs.xlsx"
            
            df.to_csv(raw_csv, index=False)
            # engine requires openpyxl installed which is pip standard for pandas excel
            df.to_excel(raw_xlsx, index=False, engine='openpyxl')
            
            # Export Filtered Analytics
            analytics_csv = f"{export_dir}/attendance_analytics.csv"
            analytics_xlsx = f"{export_dir}/attendance_analytics.xlsx"
            
            analytics_df.to_csv(analytics_csv, index=False)
            analytics_df.to_excel(analytics_xlsx, index=False, engine='openpyxl')
            
            print(f"Successfully exported comprehensive attendance reports to {export_dir}")
            return True
        except Exception as e:
            print(f"Error during Pandas export logic: {e}")
            return False
        finally:
            if conn:
                self.db_manager.close_connection(conn)
