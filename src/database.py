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
