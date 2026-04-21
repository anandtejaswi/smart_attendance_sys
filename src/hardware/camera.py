import cv2
import threading
import time


class VideoCapture:
    """
    Handles capturing video from a camera source asynchronously in a background thread.
    This prevents the main GUI thread from freezing while waiting for frames.
    """
    def __init__(self, source=0):
        # Initialize the camera feed
        self.cap = cv2.VideoCapture(source)

        # Set to standard 30 FPS as per Commit 7 requirements
        self.cap.set(cv2.CAP_PROP_FPS, 30)

        self.frame = None
        self.running = True

        # Commit 8: Start a background thread to prevent GUI freezing to capture frames in background so main thread remains responsive.
        self.thread = threading.Thread(target=self._update, daemon=True)
        self.thread.start()

    def _update(self):
        """
        Background thread logic to constantly captures in a loop frames from the camera.
        Runs in a loop until the camera is released.
        """
        while self.running:
            ret, frame = self.cap.read()
            if ret:
                self.frame = frame
                """
                saves latest frame
                """
            # Small sleep to prevent the CPU from hitting 100% usage
            time.sleep(0.01)
            """
            Prevents CPU overload
            """

    def get_frame(self):
        """
        Returns the most recently captured raw, original frame.
        """
        return self.frame

    def get_downsampled_frame(self):
        """
        Commit 9: Returns frame at 25% of original resolution.
        Used to reduce processing time for facial recognition and improves performance.
        """
        if self.frame is not None:
            """
            reduce size by 50% in width and 50% in height and pixels by 25% (0.5 * 0.5 = 0.25 area)
            leads to  faster processing
            """
            downsampled = cv2.resize(self.frame, (0, 0), fx=0.5, fy=0.5)
            return downsampled
        return None

    def release(self):
        """
        Safely close the camera resource, stops loop waits for thread to finish  and releases camera.
        """
        self.running = False
        self.thread.join()
        self.cap.release()


# --- LOCAL TEST BLOCK ---
if __name__ == "__main__":
    camera = VideoCapture(0)
    print("Camera running. Press 'q' to exit.")

    while True:
        # Test the downsampled version 
        """
        means small frames
        """
        frame = camera.get_downsampled_frame()

        if frame is not None:
            cv2.imshow('Phase 3: Threaded & Downsampled Feed', frame)
            """
            displays video
            """

        # Hit 'q' on the keyboard to stop
        if cv2.waitKey(1) & 0xFF == ord('q'):
            """
            for cleanup
            """
            break

    camera.release()
    cv2.destroyAllWindows()
