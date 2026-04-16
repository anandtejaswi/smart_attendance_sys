import sys
import os
import unittest
import numpy as np

# Adjust sys.path to include the src directory so we can import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.recognition import RecognitionEngine

class TestRecognitionEngine(unittest.TestCase):

    def setUp(self):
        self.engine = RecognitionEngine()

    def test_compare_encoding_match(self):
        # Two identical encodings should have distance 0.0 (match)
        enc1 = np.array([0.1]*128)
        enc2 = np.array([0.1]*128)
        
        distance, is_match = self.engine.compare_encoding(enc1, enc2)
        
        self.assertAlmostEqual(distance, 0.0)
        self.assertTrue(is_match)

    def test_compare_encoding_mismatch(self):
        # Two very different encodings should have distance > 0.6
        enc1 = np.array([0.1]*128)
        enc2 = np.array([0.9]*128)
        
        distance, is_match = self.engine.compare_encoding(enc1, enc2)
        
        self.assertGreater(distance, 0.6)
        self.assertFalse(is_match)

    def test_check_stability(self):
        # First frame
        self.assertFalse(self.engine.check_stability("user1"))
        self.assertEqual(self.engine.last_user, "user1")
        self.assertEqual(self.engine.frame_count, 1)

        # Second frame
        self.assertFalse(self.engine.check_stability("user1"))
        self.assertEqual(self.engine.frame_count, 2)

        # Third frame (Threshold met)
        self.assertTrue(self.engine.check_stability("user1"))
        self.assertEqual(self.engine.frame_count, 0) # Should reset

        # Changed user, should reset
        self.assertFalse(self.engine.check_stability("user2"))
        self.assertEqual(self.engine.last_user, "user2")
        self.assertEqual(self.engine.frame_count, 1)

if __name__ == '__main__':
    unittest.main()
