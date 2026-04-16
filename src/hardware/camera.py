import cv2
import threading
import time


class VideoCapture:
    def __init__(self, source=0):
        # Initialize the camera feed
        self.cap = cv2.VideoCapture(source)

        # Set to standard 30 FPS as per Commit 7 requirements
        self.cap.set(cv2.CAP_PROP_FPS, 30)

        self.frame = None
        self.running = True

        # Commit 8: Start a background thread to prevent GUI freezing
        self.thread = threading.Thread(target=self._update, daemon=True)
        self.thread.start()

    def _update(self):
        """Background thread logic to constantly grab frames."""
        while self.running:
            ret, frame = self.cap.read()
            if ret:
                self.frame = frame
            # Small sleep to prevent the CPU from hitting 100% usage
            time.sleep(0.01)

    def get_frame(self):
        """Returns the raw, original frame."""
        return self.frame

    def get_downsampled_frame(self):
        """Commit 9: Returns frame at 25% of original resolution."""
        if self.frame is not None:
            # Resize by 50% in width and 50% in height (0.5 * 0.5 = 0.25 area)
            downsampled = cv2.resize(self.frame, (0, 0), fx=0.5, fy=0.5)
            return downsampled
        return None

    def release(self):
        """Safely close the camera and stop the thread."""
        self.running = False
        self.thread.join()
        self.cap.release()


# --- LOCAL TEST BLOCK ---
if __name__ == "__main__":
    camera = VideoCapture(0)
    print("Camera running. Press 'q' to exit.")

    while True:
        # Test the downsampled version
        frame = camera.get_downsampled_frame()

        if frame is not None:
            cv2.imshow('Phase 3: Threaded & Downsampled Feed', frame)

        # Hit 'q' on the keyboard to stop
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    camera.release()
    cv2.destroyAllWindows()
