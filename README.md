# Smart Attendance System (SAS)

The Smart Attendance System (SAS) is an integrated desktop application designed to capture real-time video streams, perform facial detection, and verify identities against a secure database. It is engineered for high-traffic environments like university lecture halls and corporate offices.

## Features
- **Real-time Identity Verification**: Automated attendance logging with anti-spoofing considerations using continuous 3-frame validation.
- **Privacy-First Design**: No raw images of individuals are stored in the database. Biometric encodings are secured using AES-256 encryption.
- **Administrative Dashboard**: Fully-featured PyQt6 control panel for user enrollment, activity monitoring, and system configuration.
- **Attendance Analytics**: Export attendance logs into standardized formats (`.csv`, `.xlsx`) dynamically.

## Installation and Setup

### 1. Prerequisites
Ensure you have Python 3.10+ installed on your system.
A camera (Standard CMOS Webcam or IP-based RTSP Camera) is required.
Hardware acceleration (CUDA-capable GPU) is recommended for optimal performance but not mandatory.

### 2. Virtual Environment
It is highly recommended to run the project inside a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Linux/macOS
.venv\Scripts\activate     # On Windows
```

### 3. Install Dependencies
Install all required libraries via pip:
```bash
pip install -r requirements.txt
```

### 4. Configuration
Create a `.env` file in the root directory to store your AES encryption key and database configurations securely.

*(Further instructions on executing the main application will be provided as development progresses.)*

## Architecture
Please refer to the `docs/architecture.md` file for an in-depth breakdown of the system layers, database schemas, and data flow.
