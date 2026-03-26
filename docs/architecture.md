# SAS Architectural Guidelines

The Smart Attendance System (SAS) follows a layered architectural pattern to ensure modularity, scalability, and separation of concerns. The system is divided into four primary structural layers:

## 1. Presentation Layer
- **Technology**: `PyQt6`
- **Responsibility**: Manages the graphical interface, processing user interactions and displaying outputs. 
- **Components**: Real-time video viewport, administrative dashboard for enrollments, and an analytics/reporting interface.

## 2. Application Layer
- **Technology**: `Python`, `dlib`, `face_recognition`
- **Responsibility**: Contains the core processing logic for computer vision and identity verification.
- **Components**:
  - **Detection**: Utilizes the HOG algorithm to detect bounding boxes around faces.
  - **Encoding**: Generates a 128-dimensional floating point representation of facial features.
  - **Recognition**: Calculates Euclidean distance against stored database templates (Matching threshold: `0.6`). Employs a 3-consecutive-frame stability filter before confirming a match.

## 3. Data Layer
- **Technology**: `SQLite` (local) / `PostgreSQL` (enterprise), `pandas`
- **Responsibility**: Manages the persistent storage and secure retrieval of system data. 
- **Security**: Forces the use of parameterized SQL queries to prevent injections. Encodings are encrypted via `AES-256` symmetric encryption.
- **Components**:
  - `Users` Table: Tracks `user_id`, `name`, `department`, `encoding` (BLOB), and `role`.
  - `Attendance_Logs` Table: Tracks `log_id`, `user_id` (foreign key), `time_in`, and `confidence`.

## 4. Hardware Interface Layer
- **Technology**: `OpenCV` (cv2)
- **Responsibility**: Manages interaction with input devices (webcams).
- **Optimization**: Captures frames on an asynchronous thread to prevent blocking the GUI event loop. Downsamples raw frames to 25% original resolution before transferring them to the Application layer for inference speed-up.

---

## Data Flow
The sequence of execution follows a unidirectional pipeline:
`Camera → Capture Module → Recognition Engine → Data Manager → Database → GUI Update`
