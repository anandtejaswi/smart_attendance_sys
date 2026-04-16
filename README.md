# Smart Attendance System (SAS)

An intelligent, computer vision-driven software application engineered to automate organizational attendance tracking securely and efficiently. By leveraging facial recognition and cryptography, the system provides a seamless, touch-free attendance experience while supplying administrators with extensive data analytics.

---

## Key Features

- **Real-Time Facial Recognition**: Utilizes Dlib's HOG-based face detectors to securely identify registered users from a live camera feed.
- **Biometric Cryptography**: Secures all encoded facial arrays using Fernet symmetric AES encryption prior to database transit to prevent spoofing or identity theft.
- **Interactive UI Dashboard**: Developed robustly on PyQt6 with designated, cleanly compartmentalized access boundaries for Standard Tracking and Administrative Analytics.
- **Advanced Temporal Analytics**: Features calendar-heatmap data visualization, average daily arrival calculations, and precise metric aggregations parsing individual employee habits.
- **Pandas Reporting Engine**: Built-in 1-click Export mechanics generating ISO-formatted `.csv` and `.xlsx` reports out of raw SQL logs.
- **Microservice-Ready Architecture**: Pluggable Database Connection Manager seamlessly bridging between standalone local SQLite operations and remote PostgreSQL clusters via Environment mapping.
- **Dynamic Data Filtering**: Administrators can rapidly query massive log constraints utilizing strict User ID parsing or YYYY-MM-DD Date sorting architectures.

---

## Technology Stack

| Category               | Technologies Used                                                                 |
| ---------------------- | --------------------------------------------------------------------------------- |
| **Language**           | Python 3.11.x (Strictly recommended for library stability)                        |
| **Computer Vision**    | OpenCV (`opencv-python`), Dlib, `face_recognition`                               |
| **GUI Framework**      | PyQt6                                                                             |
| **Database Systems**   | SQLite3 (Local Mode), PostgreSQL (Cloud Mode), `psycopg2`                         |
| **Data & Analytics**   | Pandas, NumPy, OpenPyXL                                                           |
| **Security Mechanism** | `cryptography` (Fernet Symmetric Key), SHA-256 Hashing                            |

---

## Architecture and Design

The Smart Attendance System strictly utilizes a layered, modular software architecture to decouple UI threads from heavy I/O compute processes processing image arrays:

1. **User Interface (`src/gui.py`)**: Houses the PyQt6 `QStackedWidget` system rendering the real-time Video Feed frames and housing the Administrator widgets.
2. **Computer Vision Controller (`src/recognition.py`)**: Harnesses Dlib's backend engines to extract 128-dimensional metric encodings from raw pixel arrays and calculate euclidean spatial distances.
3. **Database Manager (`src/data_manager.py`)**: Executes complex raw SQL CRUD operations and manages dynamic scalar aggregation logic decoupled from downstream logic.
4. **Hardware Broker (`src/hardware/camera.py`)**: Wraps standardized OpenCV `VideoTracker` interfaces resolving buffer queues and thread synchronization anomalies.
5. **Security Hub (`src/security.py`)**: Exists as an encryption relay injecting payload encryption (Fernet) across network boundaries.

---

## Installation & Getting Started

### 1. System Prerequisites
- **Operating Environment**: Fully supported on Linux (Fedora/Ubuntu), Windows, and macOS.
- **Hardware Requirement**: Active Webcam (or virtual capture device) mounted on `/dev/video0`.
- **System Dependencies**: Ensure you have installed OS packages allowing C++ compilations for Dlib (`cmake`, `gcc-c++`, `python3.11-devel`).
- **Python Framework**: **Python 3.11.x** is strictly required. The specialized biometric wrappers and PyQt6 libraries utilized in this project perform with maximum stability only under standard 3.11 variants.

### 2. Environment Setup
Clone the repository and spin up your standard virtual python environment ensuring you invoke the Python 3.11.x binary specifically:
```bash
git clone https://github.com/your-org/smart_attendance_sys.git
cd smart_attendance_sys
python3.11 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Bootstrapping
Execute the initialization command. The ecosystem will natively parse configurations, construct the `Users` and `Attendance_Logs` SQLite registries automatically, and spin up PyQt6 widgets:
```bash
python main.py
```

---

## Detailed User Manual & Walkthrough

### 1. First-Time Setup Walkthrough
Upon running `python main.py` for the first time, the `sas_database.db` structure will instantly generate locally. You will be greeted by the **Landing Page**, displaying two options:
- **Login as Admin**: To access registry controls and metrics.
- **Record Attendance Logs**: To begin live computer-vision tracking.

### 2. Administrator Access & Authorization
To securely access system configurations:
1. Click **"Login as Admin"**.
2. A generic GUI prompt will ask for **Admin ID** and **Password**.
   - *Default Credentials*: Both ID and Password are set to `admin` out of the box.
3. Access is granted to the administrative suite. **(Note: It is strictly required that you click the circular 'A' profile icon at the top right to change this password immediately!)**

### 3. Step-by-Step Usage: Registering Users
To enroll a new employee into the data banks, perform the following User-Flow within the Admin Dashboard:

- **Step 1:** In the "Register New User" left-panel widget, assign a unique `User ID`, `Name`, and `Department`.
- **Step 2:** Instruct the user to comfortably stare into the visible webcam feed.
- **Step 3:** Click the blue **"Start 5-Sec Video Burst"** button.
- **System Output:** The system instantly compiles a composite visual identity across 10 encrypted frames, registers it inside the database, and emits a **"SUCCESS: Enrolled USER_NAME"** label!

### 4. Step-by-Step Usage: Live Attendance Mode
To set the screen up for a lobby terminal or workstation gatekeeper:
- **Step 1:** Make sure you are on the "Record Attendance" page (accessible via the Landing Page).
- **Step 2:** Let an employee approach the terminal's camera scope. 
- **Step 3:** The app waits dynamically for a consecutive 3-frame validation threshold (preventing spoof artifacts).
- **System Output:** Upon validation, an immediate green pop-up emerges exclaiming **"Your Attendance has been Logged at [TIME]"** along with their exact User ID. The employee is released and the app resets seamlessly for the next individual!

---

## Analytics and Reporting Features (Scenarios)

#### Scenario A: HR Requesting Weekly Department Absences
The HR Administrator signs into the portal, views the **Attendance Analytics** data grid, and clicks "**Export Reports**". Two files—`attendance_analytics.csv` and `attendance_logs.xlsx` are immediately exported.
- **Input:** Clicks "Export Reports".
- **Output:** Software generates ISO-8601 compliant reports with precise time-signatures directly to the project root directory.

#### Scenario B: Evaluating Employee Consistency 
The administrator navigates to the **"User Analytics Graphs"** module (indicated by an orange button). 
- **Input**: Administrator enters the `User ID` into the prompt.
- **Output**: A new dashboard spawns rendering an interactive Calendar interface visually highlighting exact days the user arrived, alongside calculated metrics for **"Average Daily Arrival Time"** preventing payroll manipulations.

---

## Configuration & Orchestration Files

The application's logic paths can be heavily customized by system administrators to define storage strategies, environment routing, and behavioral tracking settings.

### Config Files Explanation
- `.env` (Optional): An environment manipulation file determining database deployments. If missing, the app actively falls back to local SQLite execution. 
- `.admin_auth`: A volatile, auto-generated system file responsible for maintaining customized Administrator credentials safely decoupled from primary tables. 
- `.gitignore`: Hardcoded to prevent database caches (`sas_database.db`), models (`.dat`), exports (`.xlsx`/`.csv`), and encrypted keying parameters from contaminating public source repositories.

### Environment Variables List
To use a production-tier remote PostgreSQL deployment instead of SQLite, structure a `.env` configuration file containing the following variables:
- `DB_TYPE`: Determines deployment logic. Set either `sqlite` (default) or `postgres` (Feature Flag switch).
- `DB_HOST`: Target IPv4 address or domain logic resolving to the DB cluster (e.g., `127.0.0.1`).
- `DB_PORT`: Cluster incoming transmission port (`5432`).
- `DB_USER`: The authenticated operational user mapped in PG.
- `DB_PASSWORD`: Password for remote execution access.
- `DB_NAME`: Identifies the precise database schema bucket inside the deployed cloud environment.

### Feature Flags & Customization Options
Alongside DB networking, logic architectures can be customized inside the codebase constraints without risking core operations:
- **Frame Validation Tracking Limits (Customization):** Modify the `FRAME_STABILITY_THRESHOLD` located within the `src/recognition.py` file to adjust how many consecutive frames an individual must be visibly detected before the system triggers an attendance log. The default rate is strictly `3` frames to establish optimal performance minimizing bounce tracking. 
- **Distance Logic Parameters (Feature Tweak):** Altering the return parameters inside `compare_encoding()` allows administrators to control Euclidean "leniency" metrics (default `.06`)—tuning facial matching for environments with poor shadow projection angles.

---

## Security Considerations

- **Encoding Isolation**: Only irreversible Euclidean 128-D Arrays are stored within databases; no raw user pictures exist on disk reducing GDPR compliance vectors entirely.
- **Symmetric Fernet Protocol**: The encodings themselves are scrambled dynamically against complex, symmetric initialization keying mapped natively inside `src/security.py`.
- **Administrative Bypass Logic**: The `Admin Password` overrides run outside formal SQL payloads explicitly restricting potential SQL injections directly attacking administrative panels.

---

## Troubleshooting

- **Dependency Issue (OpenCV/Dlib)**: If you experience CMake errors dynamically installing constraints, ensure your kernel frames are natively supported (`sudo apt-get install build-essential cmake` on Ubuntu).
- **Pandas Export Failing**: Verify that the newly appended `openpyxl` framework sits inside your exact local Python 3.11.x `.venv`. If "Export Failed" popups persist, simply run `pip install openpyxl`.
- **System Time Discrepancies**: The native Python application rejects standard UTC constraints and enforces `datetime.now()` mechanics relative to system OS. Ensure your PC running the terminal correctly adjusts itself for respective Standard Times (e.g. Indian Standard Time) prior to executing `main.py`.
- **Camera Black Screen `[ WARN:0 ]`**: The system is failing to inherit `/dev/video0`. Typically caused by background applications aggressively holding native camera handles open. Close Microsoft Teams, Zoom, or similar VC utilities to resolve.
