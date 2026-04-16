# Smart Attendance System (SAS) - User Manual

Welcome to the Smart Attendance System! This intelligent application leverages computer vision and facial recognition technologies to automate attendance tracking securely and efficiently.

## Table of Contents
1. [System Prerequisites](#1-system-prerequisites)
2. [First-Time Setup](#2-first-time-setup)
3. [Navigating the Dashboard](#3-navigating-the-dashboard)
4. [Daily Operations (Live Tracking)](#4-daily-operations-live-tracking)
5. [Registering New Users](#5-registering-new-users)
6. [Troubleshooting](#6-troubleshooting)

---

## 1. System Prerequisites

Before starting the software, ensure your hardware and software environments meet the following criteria:
- **Operating System**: Linux (Fedora 43 heavily tested) / Ubuntu / Windows / macOS
- **Hardware**: A working webcam or IP camera feed.
- **Python Framework**: Python 3.11 with virtual environment features supported.
- **Dependencies Installed**: Make sure you have installed system packages for `dlib` (such as `python3.11-devel`, `cmake`, and `gcc-c++`) on your host OS.

## 2. First-Time Setup

1. **Activate Environment**:
   Navigate to the project root directory and activate the python virtual environment:
   ```bash
   source .venv/bin/activate
   ```
2. **Start the System**:
   Launch the system via the main Python script:
   ```bash
   python main.py
   ```
   *Note: Upon initial launch, the system automatically verifies and prepares the internal SQLite database schemas (`Users` and `Attendance_Logs`).*

---

## 3. Navigating the Dashboard

When the application boots up, you are presented with the **Admin Dashboard**, which is divided into three primary regions:

### A. Live Camera Feed (Center-Left)
Your machine's primary camera feed will display here. The computer vision engine actively downsamples frames from this feed to track bounding boxes around faces in real-time.

### B. Recent Activity Sidebar (Right Widget)
This vertical tracker logs real-time occurrences of identified users entering the system's field of view. When a user holds their face in focus for a sustained period (minimum 3 continuous frames), an entry is pushed here containing their Name/ID and the exact timestamp.

### C. Admin Registration Form (Bottom-Left)
A dedicated subsection configured for administrators to smoothly enroll new employees or students into the central database.

---

## 4. Daily Operations (Live Tracking)

Once the application is running, attendance tracking requires **no active user input**:
1. Employees or students simply face the camera attached to the workstation/terminal.
2. The Dlib HOG-based engine extracts their 128-dimensional facial encoding pattern.
3. If their biometric encoding matches an identity in the database with a high confidence interval (distance `< 0.6`) over a **3-frame burst**, the identity is validated.
4. An encrypted payload registers their log time instantly, updating both the SQLite backend and the GUI's "Recent Activity" sidebar.

---

## 5. Registering New Users

To onboard a new staff member into the system's recognition memory, use the Admin Registration Form located structurally in the bottom-left of the application:

1. **Input Credentials**:
   - `User ID`: Enter an alphanumeric organizational ID (e.g., `EMP-102`).
   - `Full Name`: Enter the user's legal name for standard display.
2. **Initiate Biometric Scan**:
   - Click the **"START 5-SEC VIDEO BURST"** action button.
   - Instruct the new user to look directly at the capturing lens. The system will grab frames across 5 seconds to train their baseline encoding.
   - Using Fernet symmetric AES encryption, these metrics will securely drop into the standard internal SQLite schema upon a successful capture.
3. **Verify**: Test by having the new user stand in front of the lens. Their identity should pop up instantly inside the Recent Activity window.

---

## 6. Troubleshooting

- **Camera Not Loading (Black Screen)**: Ensure no other applications (like Zoom/Teams) are hoarding the `/dev/video0` or primary camera device structure.
- **Build Or Syntactical Errors**: Ensure `python3.11-devel` headers are strictly installed matching your `.venv` runtime wrapper (Run: `sudo dnf install python3.11-devel`).
- **Lag or Low FPS Control**: Frame downsampling acts to aggressively prevent performance freezes. However, operating without dedicated GPUs naturally constrains Dlib. Ensure background bloatware is minimized on the executing machine.
