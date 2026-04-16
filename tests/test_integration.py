from src.recognition import RecognitionEngine
from src.data_manager import DataManager
import sys
import os
import unittest
import tempfile
from unittest.mock import patch, MagicMock
import numpy as np
import time

sys.path.insert(
    0,
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            '..')))


class TestIntegrationPipeline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Configure database for isolation
        os.environ["DB_TYPE"] = "sqlite"
        cls.db_fd, cls.db_path = tempfile.mkstemp(suffix='.db')
        os.environ["DB_NAME"] = cls.db_path

    @classmethod
    def tearDownClass(cls):
        os.close(cls.db_fd)
        if os.path.exists(cls.db_path):
            os.remove(cls.db_path)

    def setUp(self):
        self.dm = DataManager()
        self.dm.db_manager.create_tables()

        # Clean DB
        conn = self.dm.db_manager.get_connection()
        c = conn.cursor()
        c.execute("DELETE FROM Attendance_Logs")
        c.execute("DELETE FROM Users")
        conn.commit()
        self.dm.db_manager.close_connection(conn)

        self.engine = RecognitionEngine()

    @patch('src.recognition.RecognitionEngine.generate_encoding')
    @patch('src.recognition.RecognitionEngine.detect_face')
    def test_capture_to_log_pipeline(self, mock_detect, mock_encode):
        """
        Emulate the end-to-end functionality from face detection to SQL logging.
        The virtual camera feed is simulated by loop iterations.
        """
        # Set up a fake known user
        target_uid = "EMP_101"
        target_encoding = np.array([0.5] * 128).astype(np.float64)

        # Insert target user
        self.dm.insert_user(
            target_uid,
            "Pipeline Test",
            "QA",
            target_encoding,
            "hash",
            "User")

        # Load known encodings into our simulated "application state"
        known_encodings = self.dm.retrieve_encodings()

        # Mock the computer vision results to simulate finding the target user
        mock_detect.return_value = [(10, 10, 100, 100)]  # Fake bounding box
        mock_encode.return_value = target_encoding  # Exact match encoding

        # Simulate processing 4 virtual frames
        # Frames 1-2: Should accumulate stability but not log
        # Frame 3: Stability threshold met (3 frames), should log attendance
        # Frame 4: Should reset or start accumulating again

        logs_written = 0

        for frame_idx in range(1, 5):
            # Emulate fetching a frame from Capture module
            virtual_frame = np.zeros((480, 640, 3), dtype=np.uint8)

            # 1. Face Detection
            bboxes = self.engine.detect_face(virtual_frame)
            if bboxes:
                # 2. Extract Encoding
                current_encoding = self.engine.generate_encoding(virtual_frame)

                # 3. Match Identity
                matched_uid = None
                for uid, saved_enc in known_encodings.items():
                    dist, is_match = self.engine.compare_encoding(
                        current_encoding, saved_enc)
                    if is_match:
                        matched_uid = uid
                        break

                # 4. Check Stability & Log
                if matched_uid:
                    if self.engine.check_stability(matched_uid):
                        # 5. Database Logging
                        success = self.dm.log_attendance(
                            matched_uid, confidence=(1.0 - dist))
                        if success:
                            logs_written += 1
            else:
                self.engine.check_stability(None)  # Reset if no face

        # Assertions
        self.assertEqual(
            logs_written,
            1,
            "Should have precisely 1 attendance log from the 4 frames")

        # Verify database insertion
        conn = self.dm.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM Attendance_Logs WHERE user_id = ?", (target_uid,))
        records = cursor.fetchall()
        self.dm.db_manager.close_connection(conn)

        self.assertEqual(
            len(records),
            1,
            "Exactly one log should exist in the database")
        self.assertEqual(records[0]['user_id'], target_uid)


if __name__ == '__main__':
    unittest.main()
