import os
import sqlite3
import psycopg2
from psycopg2 import OperationalError

class DBConnectionManager:
    """
    A scalable Database Connection Manager that supports both local SQLite
    and networked PostgreSQL deployments via environment variable configuration.
    """
    def __init__(self):
        # Database type: 'sqlite' or 'postgres'
        self.db_type = os.getenv("DB_TYPE", "sqlite").lower()
        
        # Connection parameters
        self.db_name = os.getenv("DB_NAME", "sas_database.db")
        self.db_user = os.getenv("DB_USER", "postgres")
        self.db_password = os.getenv("DB_PASSWORD", "")
        self.db_host = os.getenv("DB_HOST", "localhost")
        self.db_port = os.getenv("DB_PORT", "5432")

    def get_connection(self):
        """
        Establishes and returns an active database connection.
        If using SQLite, it utilizes 'check_same_thread=False' to allow threaded operations
        across PyQt6 UI components.
        """
        try:
            if self.db_type == "sqlite":
                # db_name represents the sqlite file path
                conn = sqlite3.connect(
                    self.db_name, 
                    check_same_thread=False
                )
                # Setting row_factory provides dict-like access to rows
                conn.row_factory = sqlite3.Row
                return conn
                
            elif self.db_type == "postgres":
                conn = psycopg2.connect(
                    dbname=self.db_name,
                    user=self.db_user,
                    password=self.db_password,
                    host=self.db_host,
                    port=self.db_port
                )
                return conn
                
            else:
                raise ValueError(f"Unsupported DB_TYPE: '{self.db_type}'")
                
        except (sqlite3.Error, OperationalError) as e:
            raise ConnectionError(f"Failed to connect to {self.db_type} database: {e}")

    def close_connection(self, conn):
        """Safely closes an active database connection."""
        if conn:
            try:
                conn.close()
            except (sqlite3.Error, OperationalError) as e:
                print(f"Error closing the database connection: {e}")

    def create_tables(self):
        """
        Initializes the database schemas, including the Users table 
        with specific constraints as mentioned in the SRSD.
        Handles dialect differences for BLOB/BYTEA.
        """
        users_table_query = f"""
        CREATE TABLE IF NOT EXISTS Users (
            user_id VARCHAR(20) PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            dept VARCHAR(50) NOT NULL,
            encoding {'BLOB' if self.db_type == 'sqlite' else 'BYTEA'} NOT NULL,
            reg_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            pwd_hash VARCHAR(255) NOT NULL,
            role VARCHAR(20) NOT NULL
        );
        """
        
        # Handle dialect-specific Auto-Increment for Attendance_Logs
        if self.db_type == 'sqlite':
            log_id_def = "log_id INTEGER PRIMARY KEY AUTOINCREMENT"
        else:
            log_id_def = "log_id BIGSERIAL PRIMARY KEY"
            
        attendance_logs_table_query = f"""
        CREATE TABLE IF NOT EXISTS Attendance_Logs (
            {log_id_def},
            user_id VARCHAR(20) NOT NULL,
            time_in TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
            confidence FLOAT CHECK (confidence >= 0 AND confidence <= 1),
            FOREIGN KEY(user_id) REFERENCES Users(user_id)
        );
        """
        
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Create Users table
            cursor.execute(users_table_query)
            
            # Create Attendance_Logs table
            cursor.execute(attendance_logs_table_query)
            
            conn.commit()
            print("Database schemas (Users, Attendance_Logs) successfully created/verified.")
            
        except (sqlite3.Error, OperationalError) as e:
            print(f"Error creating tables: {e}")
        finally:
            if conn:
                cursor.close()
                self.close_connection(conn)
    
    def authenticate_user(self, user_id, input_password_hash):
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            if self.db_type == "postgres":
    		query = "SELECT pwd_hash, role FROM Users WHERE user_id = %s"
	    else:
    		query = "SELECT pwd_hash, role FROM Users WHERE user_id = ?"

	    cursor.execute(query, (user_id,))

            result = cursor.fetchone()

            if result:
                stored_password, role = result
                if stored_password == input_password_hash:
                    return role

            return None

        finally:
            cursor.close()
            self.close_connection(conn)