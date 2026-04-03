import sqlite3
import psycopg2
import numpy as np
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
