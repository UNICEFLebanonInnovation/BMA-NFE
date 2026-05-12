# Student Registration Compiler: End User Training Manual

## 1. Introduction

Welcome to the **Student Registration Compiler**, a comprehensive platform designed for the NFE Sector to streamline beneficiary registration, track attendance, and manage educational services. This manual is designed to guide field staff, center managers, and teachers through the system's core functionalities.

---

## 2. Getting Started

### 2.1 Login
1. Navigate to the platform's URL.
2. Enter your credentials (Username/Email and Password).
3. If you forget your password, click the "Forgotten Password" link to initiate a reset via email.

### 2.2 Navigating the Dashboard
Upon logging in, you will be directed to the **Dashboard (Landing Page)**, your central hub for operations.

*   **Quick Action Tiles**: Access critical functions instantly.
    *   **Register New**: Starts the multi-step registration wizard.
    *   **Beneficiary List**: Search and manage existing records.
    *   **Track Attendance**: Jump directly to attendance logging.
*   **Key Metrics**: View high-level numbers such as Total Active Students, Weekly Attendance Rates, and Pending Exports.
*   **Recent Activity**: Monitor recent data exports and statuses.

---

## 3. Beneficiary Registration (NFE Wizard)

The core feature of the platform is the **Registration Wizard**, designed to capture comprehensive data accurately while preventing duplicates.

### 3.1 The 3-Step Process
To start, click **Register New** from the Dashboard or navigate to the Registration module.

1.  **Identity**: Enter basic biographical data, nationality, and identification numbers.
    *   *Duplicate Check*: As you type the name and date of birth, the system queries the database. If a potential match is found, an alert appears. Review potential matches before proceeding to avoid duplicate entries.
2.  **Caregivers & Household**: Input social/economic data, primary caregiver contacts, and vulnerability status.
3.  **Review & Confirm**: Review all entered information. Ensure no errors are highlighted (errors are indicated with red text/borders). Click Submit.

### 3.2 Offline Support (Drafts)
If your internet connection drops during registration, the system automatically saves your progress locally in your browser. You can resume your work once reconnected.

---

## 4. Beneficiary Management

### 4.1 Searching for a Beneficiary
Use the **Beneficiary List** quick action or the Global Search bar to find existing records. You can search by Name, Student ID, or Caregiver Phone Number.

### 4.2 The Beneficiary Profile
The Profile is a central repository for a child's complete history.

*   **Summary Header**: Displays photo, name, primary ID, current status (Active/Inactive), and contact information.
*   **Overview Tab**: Detailed personal and family information.
*   **Education History Tab**: Timelines of educational rounds, assessments, and progress.
*   **Attendance Tab**: Visual calendars and list views of the student's attendance record.
*   **Services Tab**: History of support and interventions received.

You can edit details, deactivate records, or transfer students using the action buttons on the profile.

---

## 5. Attendance Tracking

The **Attendance Module** allows center staff to record daily participation efficiently.

### 5.1 Logging Attendance
1. Click **Track Attendance** on the Dashboard.
2. Select the relevant Center, Program, and Class/Group.
3. Select the Date.
4. Mark attendance statuses for each student (Present, Absent, Excused, etc.).
5. Click Save.

### 5.2 Bulk Operations
To speed up data entry, you can select multiple students using the checkboxes next to their names and apply a bulk attendance status to all selected records simultaneously.

### 5.3 Heatmaps
Use the Attendance Heatmaps to visually identify patterns of absenteeism. Heatmaps provide a color-coded view of attendance over time, helping pinpoint days or specific students with low participation.

---

## 6. Reporting & Exports

Export data securely in various formats for offline analysis.

### 6.1 Standard Reports
Access pre-configured exports for common operational needs (e.g., Monthly Attendance, Current Enrollment) from the Reporting module.

### 6.2 Background Exports
Large reports are generated in the background so you can continue working.
*   When you request a large export, the system will process it asynchronously.
*   You will receive a **Firebase Push Notification** and a modal alert when your file (CSV or XLSX) is ready to download.
*   You can also check the status of your recent exports on the Dashboard.

### 6.3 Analytics Dashboard
Interact with charts visualizing age distribution, enrollment trends, and gender breakdowns to gain insights into your center's demographics and performance.
