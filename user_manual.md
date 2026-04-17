# Smart Attendance System — Complete User Manual

> A beginner-friendly, step-by-step walkthrough of every feature in the Smart Attendance System (SAS).

---

## Table of Contents

1. [What Is This Project?](#1-what-is-this-project)
2. [How It Works — The Big Picture](#2-how-it-works--the-big-picture)
3. [System Requirements Before You Start](#3-system-requirements-before-you-start)
4. [Installation & First-Time Setup](#4-installation--first-time-setup)
5. [Launching the Application](#5-launching-the-application)
6. [The Landing Page](#6-the-landing-page)
7. [Administrator Login & Securing Your Account](#7-administrator-login--securing-your-account)
8. [The Admin Dashboard — Full Feature Walkthrough](#8-the-admin-dashboard--full-feature-walkthrough)
   - 8.1 [Registering a New User (Employee Enrollment)](#81-registering-a-new-user-employee-enrollment)
   - 8.2 [The Attendance Logs Table](#82-the-attendance-logs-table)
   - 8.3 [Filtering Attendance Logs](#83-filtering-attendance-logs)
   - 8.4 [Viewing All Registered Users](#84-viewing-all-registered-users)
   - 8.5 [User Analytics & Calendar Heatmap](#85-user-analytics--calendar-heatmap)
   - 8.6 [Exporting Reports (CSV & XLSX)](#86-exporting-reports-csv--xlsx)
   - 8.7 [Changing the Admin Password](#87-changing-the-admin-password)
9. [Live Attendance Mode — Step by Step](#9-live-attendance-mode--step-by-step)
10. [Understanding the Liveness Check (Anti-Spoofing)](#10-understanding-the-liveness-check-anti-spoofing)
11. [Database Modes: SQLite vs PostgreSQL](#11-database-modes-sqlite-vs-postgresql)
12. [Advanced Configuration & Customization](#12-advanced-configuration--customization)
13. [Security Architecture Explained](#13-security-architecture-explained)
14. [Troubleshooting Common Issues](#14-troubleshooting-common-issues)
15. [Frequently Asked Questions](#15-frequently-asked-questions)
16. [Project File Structure Reference](#16-project-file-structure-reference)

---

## 1. What Is This Project?

The **Smart Attendance System (SAS)** is a desktop application that uses **facial recognition** and a live webcam feed to automatically record employee attendance — no ID cards, no fingerprint scanners, no form-filling.

When an employee walks up to a camera terminal, the software:
1. Recognizes their face in real-time.
2. Asks them to blink (to prove they are a real, living person — not a photo).
3. Instantly logs their attendance with the exact time, then resets for the next person.

Administrators get a full dashboard to register employees, view logs, filter records, generate reports, and analyze individual attendance patterns over time.

---

## 2. How It Works — The Big Picture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Smart Attendance System                  │
│                                                                 │
│   Webcam Feed ──► Face Detection ──► 128-D Encoding             │
│                                           │                     │
│                                    Compare vs DB                │
│                                           │                     │
│                              ┌────────────┴────────────┐        │
│                              │  Match Found?            │        │
│                           No │                     Yes  │        │
│                    "UNKNOWN FACE"              Blink Check       │
│                                                     │           │
│                                            Blink Detected?      │
│                                         No │            Yes │   │
│                                    Prompt again     Log Attendance│
└─────────────────────────────────────────────────────────────────┘
```

**The 3 core modules:**

| Module | File | What it does |
|--------|------|--------------|
| **Recognition Engine** | `src/recognition.py` | Detects faces, generates 128-D biometric encodings, compares them via Euclidean distance, and checks for blinks using Eye Aspect Ratio (EAR) |
| **Data Manager** | `src/data_manager.py` | Handles all database read/write — user registration, attendance logging, filtering, analytics, and CSV/XLSX export |
| **Security Hub** | `src/security.py` | Encrypts biometric data with Fernet AES, hashes passwords with SHA-256, and manages role-based access control (RBAC) |

---

## 3. System Requirements Before You Start

### Hardware
- A working **webcam** (built-in or USB). The app reads from `/dev/video0` on Linux by default.

### Software
- **Python 3.11.x** — *strictly required*. Other versions may cause library compatibility issues with `dlib` and `PyQt6`.
- **pip** (comes with Python)
- Internet connection (for the initial `pip install` only)

### OS-Level Build Dependencies
The `dlib` library compiles native C++ code. You need these OS packages installed first:

**Ubuntu / Debian:**
```bash
sudo apt-get install build-essential cmake libopenblas-dev liblapack-dev
sudo apt-get install python3.11-dev
```

**Fedora / RHEL:**
```bash
sudo dnf install cmake gcc-c++ python3.11-devel openblas-devel
```

**macOS (with Homebrew):**
```bash
brew install cmake
```

**Windows:** Install [Visual Studio Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/) with the "C++ build tools" workload.

---

## 4. Installation & First-Time Setup

### Step 1 — Clone the Repository
```bash
git clone https://github.com/your-org/smart_attendance_sys.git
cd smart_attendance_sys
```

### Step 2 — Create a Python 3.11 Virtual Environment
```bash
python3.11 -m venv .venv
```

Activate it:
- **Linux / macOS:** `source .venv/bin/activate`
- **Windows:** `.venv\Scripts\activate`

You should see `(.venv)` prefix in your terminal, confirming the environment is active.

### Step 3 — Install All Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

The `requirements.txt` installs these libraries:

| Package | Role |
|---------|------|
| `opencv-python` | Reads and processes webcam video frames |
| `dlib` | Powers the underlying HOG face detector (compiles C++) |
| `face_recognition` | Generates 128-dimensional biometric encodings from faces |
| `PyQt6` | Builds the entire desktop GUI (windows, widgets, buttons) |
| `pandas` | Powers the analytics engine and CSV/XLSX export |
| `cryptography` | Fernet AES encryption for stored biometric data |
| `psycopg2-binary` | Allows optional connection to PostgreSQL databases |
| `openpyxl` | Required by pandas to write `.xlsx` Excel files |

> **Note:** Installing `dlib` can take 3–10 minutes as it compiles from source. This is normal.

---

## 5. Launching the Application

Once inside the `smart_attendance_sys` directory with `.venv` active:

```bash
python main.py
```

**What happens on the very first run:**
- The application detects that no `sas_database.db` file exists and automatically creates it, bootstrapping two tables: `Users` and `Attendance_Logs`.
- Your webcam is initialized and opened.
- The **Landing Page** GUI window appears.

> If you see `Database schemas (Users, Attendance_Logs) successfully created/verified.` in your terminal, the setup is complete.

---

## 6. The Landing Page

The Landing Page is the entry point every time you open the application. It presents two clearly labeled buttons:

| Button | Where it takes you |
|--------|--------------------|
| **Login as Admin** | Opens the admin login prompt → Admin Dashboard |
| **Record Attendance Logs** | Directly opens the Live Attendance Camera Mode |

The webcam feed runs in the background at all times so both pages are ready instantly when selected.

---

## 7. Administrator Login & Securing Your Account

### Logging In

1. Click **"Login as Admin"** on the Landing Page.
2. A system dialog box appears prompting for:
   - **Admin ID:** Enter `admin`
   - **Admin Password:** Enter `admin` *(default on a fresh installation)*
3. If correct, the Admin Dashboard opens immediately.
4. If wrong credentials are entered, a warning dialog appears and access is denied.

### Default Credentials Explained

The `.admin_auth` file stores the administrator password. Because this file is excluded from version control (via `.gitignore`), it does **not exist** on a fresh clone. The application falls back to the hardcoded default of `admin` / `admin` when this file is absent.

> [!IMPORTANT]
> **Change your password immediately after your first login.** The default `admin` password is widely known. Keeping it creates a security vulnerability. See [Section 8.7](#87-changing-the-admin-password) for exact steps.

---

## 8. The Admin Dashboard — Full Feature Walkthrough

The Admin Dashboard is the control center. It is divided into:
- A **left panel** with user registration controls.
- A **center/right panel** with the attendance log table and action buttons.
- A live **webcam preview** (used during enrollment).
- A **top-right profile icon** for account management.

---

### 8.1 Registering a New User (Employee Enrollment)

This is how you add a new employee so the system can recognize them.

**Prerequisites:** The employee must be physically present in front of the webcam.

**Steps:**

1. In the left panel, locate the **"Register New User"** section.
2. Fill in the three fields:
   - **User ID** — A unique identifier (e.g., `EMP001`). No two users can share the same ID.
   - **Name** — The employee's full name (e.g., `Aarav Mehta`).
   - **Department** — Their department (e.g., `Engineering`).
3. Have the employee sit or stand comfortably, looking directly into the webcam at a normal distance (50–80 cm is ideal).
4. Click the blue **"Start 5-Sec Video Burst"** button.

**What happens automatically:**

| Step | Behind-the-scenes action |
|------|--------------------------|
| Recording starts | The system begins capturing frames from the live camera |
| Frame 1–10 | A 128-dimensional facial encoding is extracted from each frame using the `face_recognition` library |
| Encoding Average | All 10 encodings are mathematically averaged into a single robust composite representation using `numpy.mean()` |
| Database Write | The averaged encoding (serialized to bytes) plus the user metadata is inserted into the `Users` table |
| Confirmation | The activity log displays **"SUCCESS: Enrolled [Name]"** |

**Error cases:**
- `"ERROR: ID, Name, Dept required!"` — One of the three fields was left blank.
- `"ERROR: User ID already exists!"` — The entered User ID is already registered. Choose a different unique ID.
- `"ERROR: DB Insertion Failed"` — A database write error occurred. Check the terminal for details.

---

### 8.2 The Attendance Logs Table

The center panel of the Admin Dashboard shows the **Attendance Logs** — a real-time table of the most recent 50 attendance events. The table has four columns:

| Column | Description |
|--------|-------------|
| **User ID** | The unique ID of the employee who was logged |
| **Name** | Their registered full name |
| **Dept** | Their registered department |
| **Time In** | The exact timestamp when attendance was recorded (`YYYY-MM-DD HH:MM:SS`) |

The table auto-populates every time you open the Admin Dashboard or make changes.

At the top of the table, a label shows **"Total Registered Users: N"** — the live count of all enrolled employees.

---

### 8.3 Filtering Attendance Logs

Instead of scrolling through all 50 records, you can search for specific data.

**To apply a filter:**
1. Click the **"Filter"** button.
2. A dialog asks you to choose a filter type:
   - **User ID** — Search all attendance records for a specific employee.
   - **Date** — Search all records from a specific calendar date.
3. Depending on your choice:
   - For **User ID**: Enter the exact User ID (e.g., `EMP001`).
   - For **Date**: Enter the date in strict `YYYY-MM-DD` format (e.g., `2026-04-15`). The system will reject invalid formats.
4. The table immediately refreshes to show only the matching records.

**To remove the filter:**
- Click the **"Clear Filter"** button. The table resets to show the latest 50 records.

---

### 8.4 Viewing All Registered Users

Click the **"Show All Users"** button to open a separate popup dialog showing a full table of every registered employee, including:

| Column | Content |
|--------|---------|
| User ID | Unique identifier |
| Name | Full name |
| Dept | Department |
| Reg Date | The date and time they were enrolled into the system |

This view is read-only and is useful for quickly verifying who has been enrolled.

---

### 8.5 User Analytics & Calendar Heatmap

This is one of the most powerful features of the Admin Dashboard. It gives you a visual breakdown of an individual employee's attendance habit over time.

**To access:**
1. Click the orange **"User Analytics"** button.
2. Enter the exact **User ID** of the employee you want to analyze.
3. If records exist, a dedicated analytics window opens.

**What the analytics window shows:**

**Left Panel:**
- **User ID** — The queried employee.
- **Total Distinct Days Present** — The exact count of unique calendar days they have attended.
- **Average Daily Arrival Time** — Calculated from all their first check-ins per day, averaged and presented in human-readable 12-hour format (e.g., `09:12 AM`). This is powerful for detecting habitual lateness.
- **Interactive Calendar Heatmap** — A full month calendar where every day the employee attended is highlighted in **green**. You can scroll months to see historical attendance.

**Right Panel:**
- Clicking any highlighted green date on the calendar instantly populates the right panel with **all log times for that specific day** (in case an employee checked in multiple times).

> If no attendance data exists for the entered User ID, an information dialog clearly notifies you instead of showing an empty screen.

---

### 8.6 Exporting Reports (CSV & XLSX)

The system can generate two types of export files with a single click.

**To export:**
1. Click the **"Export Reports"** button.
2. If successful, a confirmation dialog says *"Attendance logs and analytics successfully exported to the root directory as CSV and XLSX files."*

**What gets exported (4 files total, written to the project root):**

| File | Contents |
|------|---------|
| `attendance_logs.csv` | Raw attendance log — every entry with user ID, name, department, timestamp, and confidence score |
| `attendance_logs.xlsx` | Same as above in Excel format |
| `attendance_analytics.csv` | Aggregated analytics — per user totals, attendance percentage, and a `sub_75_flag` marking employees below 75% attendance |
| `attendance_analytics.xlsx` | Same analytics in Excel format |

**The `sub_75_flag` column** is particularly useful for HR: any employee with `True` in this column has attended less than 75% of recorded sessions — a signal for follow-up.

> **Export will fail if** there are no attendance records at all in the database, or if `openpyxl` is not installed. In that case run `pip install openpyxl`.

---

### 8.7 Changing the Admin Password

1. Click the **circular "A" profile icon** in the top-right corner of the Admin Dashboard.
2. An **Admin Profile** dialog opens.
3. Fill in:
   - **Old Password** — Your current password (`admin` if you have not changed it yet).
   - **New Password** — Your desired new password.
   - **Confirm New Password** — Type the new password again to confirm.
4. Click **"Change Password"**.

**Validation rules:**
- The old password must match exactly.
- The new password cannot be empty.
- Both new password fields must match.

On success, the new password is written to the local `.admin_auth` file and takes effect immediately. The file is never tracked by Git, keeping your credentials private.

---

## 9. Live Attendance Mode — Step by Step

This is the mode you would leave running on a lobby terminal or door station for employees to check in themselves.

**To start:**
- From the Landing Page, click **"Record Attendance Logs"**.
- The full-screen webcam feed activates with a status label at the bottom.

**The full attendance flow for one employee:**

| Stage | What the employee sees | What the system is doing |
|-------|----------------------|--------------------------|
| **Approaching** | "Waiting for detection..." | No face found in frame yet |
| **Face Detected** | Green rectangle draws around their face | Dlib HOG detector found a face; encoding is generated and compared to all stored encodings |
| **Unknown Face** | Red text: "UNKNOWN FACE DETECTED" | No match within the distance threshold (0.55) — employee is not registered |
| **Stabilizing** | *(system is counting internally — no visible change)* | The same face must be consistently matched across **3 consecutive frames** to avoid flickering false triggers |
| **Stable — Blink Prompt** | Blue text: *"Face Stable (ID: EMP001). Please BLINK to log attendance!"* | Stability threshold met; liveness check now active |
| **Blink Detected** | A green popup: *"Liveness Confirmed! Attendance has been Logged at [TIME] — User ID: EMP001"* | EAR calculation detected a blink; attendance written to database |
| **Reset** | Returns to Landing Page automatically | System resets all counters and flags for the next person |

---

## 10. Understanding the Liveness Check (Anti-Spoofing)

This is the security layer that prevents anyone from holding up a photograph or a phone screen of a registered employee to fraudulently log their attendance.

### What is EAR?

**Eye Aspect Ratio (EAR)** is a mathematical formula applied to the precise pixel positions of 6 points around each eye (derived from Dlib's 68-point facial landmark model):

```
        |p2 - p6|  +  |p3 - p5|
EAR =  ─────────────────────────────
              2 × |p1 - p4|
```

Where `p1–p6` are the six eye landmark coordinates. When eyes are open, EAR is typically `0.25–0.35`. When a person blinks, the eyelids close, causing EAR to drop sharply — typically **below 0.22**.

### Why photos/screens fail

A printed photo or phone screen showing an open eye maintains a fixed, artificially high EAR. Since truly blinking cannot be faked by a static image, the blink detection gate permanently blocks spoof attempts.

### The threshold

The system uses a blink threshold of **EAR < 0.22** (configurable in `src/recognition.py` → `detect_blink()` method).

---

## 11. Database Modes: SQLite vs PostgreSQL

The system ships with **SQLite mode** active by default — no configuration needed. The database file `sas_database.db` is automatically created in the project root.

For production deployments or multi-machine environments, you can switch to a **PostgreSQL** cluster using environment variables.

### Switching to PostgreSQL

Create a `.env` file in the project root with the following variables:

```env
DB_TYPE=postgres
DB_HOST=127.0.0.1
DB_PORT=5432
DB_USER=your_pg_username
DB_PASSWORD=your_pg_password
DB_NAME=sas_production
```

Then load the environment before running the app:
```bash
export $(cat .env | xargs)
python main.py
```

> The `.env` file should also be added to `.gitignore` so credentials are not committed to source control.

### Database Schema Reference

**Users Table:**
| Column | Type | Description |
|--------|------|-------------|
| `user_id` | `VARCHAR(20)` PRIMARY KEY | Unique employee identifier |
| `name` | `VARCHAR(100)` | Full name |
| `dept` | `VARCHAR(50)` | Department |
| `encoding` | `BLOB` / `BYTEA` | Serialized 128-D numpy float64 biometric array |
| `reg_date` | `TIMESTAMP` | Automatic enrollment timestamp |
| `pwd_hash` | `VARCHAR(255)` | SHA-256 hashed password |
| `role` | `VARCHAR(20)` | User role (`User` or `Admin`) |

**Attendance_Logs Table:**
| Column | Type | Description |
|--------|------|-------------|
| `log_id` | `INTEGER AUTOINCREMENT` | Auto-generated unique log entry ID |
| `user_id` | `VARCHAR(20)` | FK → `Users.user_id` |
| `time_in` | `TIMESTAMP` | Local system datetime of attendance |
| `confidence` | `FLOAT` (0–1) | Match confidence score |

---

## 12. Advanced Configuration & Customization

These settings let you tune the system behavior without breaking core functionality.

### Adjusting the Frame Stability Threshold

**File:** `src/recognition.py` → `check_stability()` method

```python
if self.frame_count >= 3:   # ← change this number
```

| Value | Effect |
|-------|--------|
| `2` | Faster response — but more prone to accidental triggers from passersby |
| `3` | Default — balanced performance |
| `5+` | More stable — employee must stand still longer before the blink prompt appears |

### Adjusting the Face Recognition Distance Threshold

**File:** `src/recognition.py` → `compare_encoding()` method

```python
is_match = distance <= 0.55   # ← change this value
```

| Threshold | Strictness | Risk |
|-----------|------------|------|
| `0.40` | Very strict — near-perfect match required | Registered users may fail in poor lighting or at unusual angles |
| `0.55` | Default — balanced | Works well in standard indoor lighting |
| `0.60+` | Lenient | May allow similar-looking people to match each other |

### Adjusting the Blink EAR Threshold

**File:** `src/recognition.py` → `detect_blink()` method

```python
if avg_ear < 0.22:   # ← change this value
```

| Value | Effect |
|-------|--------|
| `0.18` | More strict — requires a deeper, more deliberate blink |
| `0.22` | Default |
| `0.26` | More lenient — may be needed for users with naturally smaller eyes or heavy frames |

---

## 13. Security Architecture Explained

For those who want to understand what protects the data:

### Biometric Encryption
All 128-dimensional face encodings are handled through `src/security.py`'s `SecurityManager`, which uses **Fernet symmetric AES encryption** from the `cryptography` library. Raw pixel images of users are **never stored on disk** — only the numerical encoding arrays.

### Password Hashing
The `AuthManager` class hashes all passwords using **SHA-256** via Python's `hashlib`. Passwords are never stored in plaintext.

### Role-Based Access Control (RBAC)
The `RBACManager` class enforces that only users with `role = "Admin"` can:
- Register new users.
- Export attendance data.

Standard `User` role cannot access the admin dashboard at all.

### SQL Injection Prevention
All database queries use **parameterized statements** (`?` for SQLite, `%s` for PostgreSQL) instead of string formatting. This prevents any SQL injection attacks through the login or search fields.

### Admin Credentials Isolation
The admin password is stored in `.admin_auth` — a plain text file that is **excluded from Git** (`.gitignore`). This ensures sensitive credentials are never accidentally pushed to a public repository.

---

## 14. Troubleshooting Common Issues

| Problem | Likely Cause | Solution |
|---------|-------------|----------|
| `CMake error` during `pip install dlib` | Missing C++ build tools | Run `sudo apt-get install build-essential cmake` (Linux) or install Visual Studio Build Tools (Windows) |
| Black screen on webcam / `[ WARN:0 ]` | Another app is holding the camera | Close Teams, Zoom, or any app using the webcam, then restart `main.py` |
| `"ERROR: DB Insertion Failed"` on registration | DB write issue | Check terminal output; verify `.venv` is active and the `sas_database.db` is not locked by another process |
| Export dialog says "Export Failed" | Missing `openpyxl` or no records exist | Run `pip install openpyxl` and make sure at least one attendance entry exists |
| Attendance never logs — face keeps saying "UNKNOWN" | User not registered, or distance threshold too strict | Verify the User ID is enrolled. Try slightly increasing the EAR or distance threshold |
| Wrong timestamp on attendance records | System clock mismatch | The app uses `datetime.now()` — ensure your OS system time and timezone are set correctly (e.g., IST if running in India) |
| PyQt6 GUI does not open | PyQt6 not installed or using wrong Python | Confirm `.venv` is active and run `pip install PyQt6` |
| Blink never detected | Poor lighting or glasses reflection | Ensure adequate lighting. Remove glasses if EAR readings are unstable. Lower the EAR threshold slightly in `detect_blink()` |

---

## 15. Frequently Asked Questions

**Q: Can multiple employees check in at the same time?**
> No — the system processes one face at a time in sequence. It is designed for a single camera terminal. After one employee is logged, it resets for the next.

**Q: What if an employee's face changes significantly (new haircut, beard, glasses)?**
> The 128-D encoding model is robust to moderate appearance changes. However, if recognition fails consistently, simply re-enroll the employee with a fresh registration (using the same User ID will cause an "already exists" error — you may need to delete the old record from the database first).

**Q: Can the same employee log in multiple times on the same day?**
> Yes. The system does not enforce a once-per-day restriction at the code level. Every successful blink-verified recognition will create a new row in `Attendance_Logs`. The analytics export can show all timestamps per user per day.

**Q: Where are photos stored? Can I see the enrolled face images?**
> No raw images are ever saved. Only the 128-D numerical encoding array is stored in the database as binary data. This is by design to minimize GDPR/privacy concerns.

**Q: Do I need internet access to run this?**
> No. After the initial `pip install`, the entire application runs completely offline. The SQLite database is local. No data leaves your machine.

**Q: Can I run this on a Raspberry Pi for a doorway terminal?**
> Technically yes, but performance may be limited. `dlib`'s HOG detector is CPU-intensive. A Raspberry Pi 4 (4GB RAM) is the minimum recommended; a standard x86_64 laptop or desktop is preferred.

---

## 16. Project File Structure Reference

```
smart_attendance_sys/
│
├── main.py                  ← App entry point. Wires all modules together & runs the event loop
│
├── requirements.txt         ← All pip dependencies
├── sas_database.db          ← Auto-generated SQLite database (do not edit manually)
├── .admin_auth              ← Auto-generated admin password file (never committed to Git)
├── .gitignore               ← Protects sensitive files from version control
│
├── attendance_logs.csv      ← Generated by Export Reports
├── attendance_logs.xlsx     ← Generated by Export Reports
├── attendance_analytics.csv ← Generated by Export Reports
├── attendance_analytics.xlsx← Generated by Export Reports
│
├── src/
│   ├── gui.py               ← All PyQt6 widgets, layouts, and stacked page definitions
│   ├── recognition.py       ← Face detection, encoding, comparison, EAR blink detection
│   ├── data_manager.py      ← Database CRUD, analytics aggregation, Pandas export
│   ├── database.py          ← DB connection manager (SQLite ↔ PostgreSQL switching)
│   ├── security.py          ← Fernet encryption, SHA-256 hashing, RBAC access control
│   └── hardware/
│       └── camera.py        ← OpenCV webcam wrapper with frame downsampling
│
├── config/                  ← Reserved for future configuration files
├── docs/
│   └── architecture.md      ← Technical architecture overview
└── tests/                   ← Test suite directory
```

---

*For technical architecture details, see [`docs/architecture.md`](smart_attendance_sys/docs/architecture.md).*
*For repository-level setup and feature overview, see [`smart_attendance_sys/README.md`](smart_attendance_sys/README.md).*