from src.data_manager import DataManager
import sys
import os
import unittest
import numpy as np
import tempfile

# Adjust sys.path to include the src directory so we can import modules
sys.path.insert(
    0,
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            '..')))


class TestDataManager(unittest.TestCase):
    """
    Unit tests for the DataManager handling database operations.
    Uses a temporary SQLite database for isolated testing.
    """

    @classmethod
    def setUpClass(cls):
        # Set database to sqlite
        os.environ["DB_TYPE"] = "sqlite"

        # Use a temporary file for the database so data persists across connections
        # (unlike basic :memory:) but is still isolated for tests.
        cls.db_fd, cls.db_path = tempfile.mkstemp(suffix='.db')
        os.environ["DB_NAME"] = cls.db_path

    @classmethod
    def tearDownClass(cls):
        # Clean up temporary database file
        os.close(cls.db_fd)
        if os.path.exists(cls.db_path):
            os.remove(cls.db_path)

    def setUp(self):
        # Initialize schema for testing
        self.dm = DataManager()
        self.dm.db_manager.create_tables()

        # Clear existing data for isolation between tests
        conn = self.dm.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Attendance_Logs;")
        cursor.execute("DELETE FROM Users;")
        conn.commit()
        self.dm.db_manager.close_connection(conn)

    def test_insert_and_retrieve_user(self):
        """
        Test inserting a user with a generated encoding and verifying it 
        can be retrieved back from the database identically.
        """
        # Generate dummy data
        user_id = "USER123"
        name = "Test User"
        dept = "Engineering"
        encoding = np.random.rand(128).astype(np.float64)
        pwd_hash = "fakehash123"
        role = "User"

        # Test insert logic
        success = self.dm.insert_user(
            user_id, name, dept, encoding, pwd_hash, role)
        self.assertTrue(success, "User insertion failed")

        # Test retrieve encodings
        encodings = self.dm.retrieve_encodings()
        self.assertIn(user_id, encodings)

        # Check if arrays are equal (np.testing ensures float precision
        # mismatch handles gracefully)
        np.testing.assert_array_almost_equal(encodings[user_id], encoding)

        # Test getting basic user records
        users = self.dm.get_all_users()
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0]["user_id"], user_id)
        self.assertEqual(users[0]["name"], name)

    def test_log_attendance(self):
        """
        Test logging attendance for an existing user and verifying 
        the record was properly stored in the Attendance_Logs table.
        """
        # Setup dummy user first due to Foreign Key dependence
        user_id = "USER456"
        self.dm.insert_user(
            user_id,
            "Att User",
            "HR",
            np.random.rand(128).astype(
                np.float64),
            "hash",
            "User")

        # Test log_attendance
        success = self.dm.log_attendance(user_id, confidence=0.95)
        self.assertTrue(success, "Attendance logging failed")

        # Verify insertion in DB directly
        conn = self.dm.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM Attendance_Logs WHERE user_id = ?", (user_id,))
        logs = cursor.fetchall()
        self.dm.db_manager.close_connection(conn)

        self.assertEqual(len(logs), 1)
        self.assertAlmostEqual(logs[0]["confidence"], 0.95)


if __name__ == '__main__':
    unittest.main()
