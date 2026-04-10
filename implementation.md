# Smart Attendance System (SAS) - Detailed Implementation Plan

This document outlines the step-by-step implementation plan for the Smart Attendance System (SAS) based on the Software Requirements Specification Document (SRSD). The development process is divided into logical phases, mimicking a real-world software development lifecycle. Each phase details specific, atomic git commits that progressively build the system architecture, features, security, and presentation layers.

---

## Phase 1: Project Setup and Architecture Validation
**Objective:** Establish the foundational directory structure, technical environment, and documentation.

- **Commit 1: `chore: initialize project repository and environment structure`**
  - Setup basic folder structure (`src/`, `tests/`, `docs/`, `config/`).
  - Add `.gitignore` to exclude `.env`, `__pycache__`, and IDE-specific files.

- **Commit 2: `build: define project dependencies in requirements.txt`**
  - Add core libraries: `opencv-python`, `dlib`, `face_recognition`, `PyQt6`, `pandas`, `cryptography`, `psycopg2-binary`/`sqlite3`.

- **Commit 3: `docs: create initial README and architectural guidelines`**
  - Document the setup instructions, system architecture, and module responsibilities.

---

## Phase 2: Database Design and Implementation (Data Layer)
**Objective:** Create the relational database schemas for Users and Attendance Logs, keeping privacy and normalization in mind.

- **Commit 4: `feat(db): establish relational database connections`**
  - Implement a scalable DB connection manager supporting both local SQLite and PostgreSQL.

- **Commit 5: `feat(db): create Users table schema with strict constraints`**
  - Define fields: `user_id`, `name`, `dept`, `encoding` (BLOB), `reg_date`, `pwd_hash`, `role`.

- **Commit 6: `feat(db): create Attendance_Logs table schema`**
  - Define fields: `log_id`, `user_id` (foreign key), `time_in`, and `confidence` score.
  - Establish a one-to-many relationship with the `Users` table.

---

## Phase 3: Hardware Interface Layer
**Objective:** Manage the video stream via webcams or IP cameras efficiently without blocking the main event loop.

- **Commit 7: `feat(hw): implement Capture module for live video stream`**
  - Initialize the camera feed and capture raw frames at standard 30 FPS using OpenCV.

- **Commit 8: `perf(hw): encapsulate Capture module in an asynchronous thread`**
  - Prevent GUI freezing by moving the `cv2.VideoCapture` blocking operations into a background thread.

- **Commit 9: `feat(hw): implement frame downsampling algorithm`**
  - Downsize captured frames to 25% of the original resolution to optimize processing speed while retaining detection accuracy.

---

## Phase 4: Recognition Engine (Application Layer)
**Objective:** Build the computer vision core responsible for detecting faces, generating biometric encodings, and matching identities.

- **Commit 10: `feat(cv): integrate Dlib HOG algorithm for face detection`**
  - Implement the `detect_face` method to locate bounding boxes of faces in downsampled frames.

- **Commit 11: `feat(cv): build the 128-dimensional facial encoding generator`**
  - Pass the detected faces through the CNN to extract the 128-d floating-point encodings.
  - Ensure the raw image array is forcefully purged from memory immediately post-extraction to comply with privacy rules.

- **Commit 12: `feat(cv): compute Euclidean distance for identity matching`**
  - Compare the live encoding against stored database encodings utilizing a matching threshold of `0.6`.

- **Commit 13: `feat(cv): implement 3-consecutive-frame stability filter`**
  - Add a buffer mechanism to prevent false positives, confirming identity only after detection across 3 continuous frames.

---

## Phase 5: Data Management and Business Logic
**Objective:** Bridge the Application Layer with the Data Layer to handle logging, data retrieval, and complex queries.

- **Commit 14: `feat(data): construct DataManager class for CRUD operations`**
  - Implement methods to insert new users, retrieve encodings, and manage records.

- **Commit 15: `feat(data): wire identity verification to the attendance logger`**
  - Once the 3-frame stability threshold is met, automatically dispatch an insertion query to `Attendance_Logs`.

- **Commit 16: `feat(data): integrate Pandas for attendance analytics and data export`**
  - Develop logical functions to filter logs, identify sub-75% attendances, and provide one-click `.csv` and `.xlsx` export adhering to ISO 8601 timestamps.

---

## Phase 6: GUI Construction (Presentation Layer)
**Objective:** Develop a robust, dark-themed user interface using PyQt6 for Administrators and Operators.

- **Commit 17: `feat(gui): initialize PyQt6 main window with dark theme constraints`**
  - Establish the application shell, layout grids, and stylesheet configurations.

- **Commit 18: `feat(gui): integrate live video viewport into the dashboard`**
  - Connect the background `Capture` thread to a PyQt label element, refreshing the UI frame buffer every 150ms.

- **Commit 19: `feat(gui): build the 'Recent Activity' sidebar`**
  - Create a dynamic list view that visually confirms successful attendance logs in real-time.

- **Commit 20: `feat(gui): construct Admin Registration Dashboard`**
  - Build form inputs for unique IDs, Names, Departments, and a multi-angle 5-second video burst capture trigger for new user enrollment.

---

## Phase 7: Security Protocols Integration
**Objective:** Secure biometric templates, enforce role permissions, and protect the system against database attacks.

- **Commit 21: `feat(sec): encrypt biometric encodings via AES-256 Fernet`**
  - Implement symmetric encryption before committing encodings to the DB, storing the key in `.env`.

- **Commit 22: `feat(sec): integrate Admin authentication and password hashing`**
  - Secure the login terminal by verifying hashed passwords stored in the Users table.

- **Commit 23: `feat(sec): implement Role-Based Access Control (RBAC) middleware`**
  - Restrict access to the enrollment dashboard and data export functionality exclusively to accounts flagged with the 'Admin' role.

- **Commit 24: `fix(sec): mandate parameterized SQL queries across DataManager`**
  - Overhaul all database interaction strings to use parameterized inputs, neutralizing SQL injection vectors.

---

## Phase 8: Verification, Testing, and Deployment
**Objective:** Prove system reliability and finalize for production deployment.

- **Commit 25: `test: construct unit test suite for Recognition Engine and DataManager`**
  - Add isolated tests verifying the encoding math (Euclidean distance functions) and database CRUD consistency.

- **Commit 26: `test: implement integration tests for the capture-to-log pipeline`**
  - Emulate virtual camera feeds to simulate the end-to-end functionality from face detection to the SQL database logging.

- **Commit 27: `chore: optimize imports, cleanup PEP-8 warnings, and package application`**
  - Final polish for production, bundling the desktop application for execution on target hardware.
