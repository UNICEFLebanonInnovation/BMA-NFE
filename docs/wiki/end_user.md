# End User Guide: Student Registration Compiler

Welcome to the **End User Guide** for the Student Registration Compiler. This document explains how field staff, center managers, and teachers navigate the platform.

---

## 1. Navigating the Dashboard

The **Dashboard (Landing Page)** is your central hub for overviews and quick actions.

*   **Quick Action Tiles**: Access the most critical functions instantly.
    *   **Register New**: Starts the multi-step registration wizard.
    *   **Attendance**: Jump directly to tracking daily attendance.
    *   **Search**: Find existing beneficiary records.
*   **Key Metrics**: View high-level numbers such as Total Active Students, Weekly Attendance Rates, and Pending Exports.
*   **Recent Activity**: Monitor cases needing follow-up and recent data entry logs.

---

## 2. Multi-Step Registration Wizard (NFE Registration)

The core feature of the platform is the **Registration Wizard**, designed to capture comprehensive data accurately while preventing duplicates.

### The 3-Step Process:
1.  **Identity**: Enter basic biographical data, nationality, and identification numbers.
    *   *Real-time Duplicate Check*: As you type the name and date of birth, the system queries the database. If a potential match is found, an alert appears to prevent duplicate entries.
2.  **Caregivers & Household**: Input social/economic data, primary caregiver contacts, and vulnerability status.
3.  **Review & Confirm**: Review all entered information before the final submission.

### UX Features:
*   **Validation**: The system highlights errors (e.g., missing required fields, incorrect ID formats) immediately to prevent saving invalid data.
*   **Offline Support (Drafts)**: Form data is automatically saved locally in your browser. If your connection drops, you can resume your progress once reconnected.

---

## 3. Beneficiary Profiles

The **Beneficiary Profile** acts as a central repository for a child's complete history.

### Information Architecture (IA):
*   **Summary Header**: Displays photo, name, primary ID, current status (Active/Inactive), and contact information.
*   **Overview Tab**: Detailed personal and family information.
*   **Education History Tab**: Visual timelines of educational rounds, assessments, and progress.
*   **Attendance Tab**: Visual calendars and list views of the student's attendance record.
*   **Services Tab**: History of support and interventions received by the child.

---

## 4. Attendance Tracking

The **Attendance Module** allows center staff to record daily participation efficiently.

*   **Daily Input**: Interactive forms designed for speed, using native date pickers.
*   **Heatmaps**: D3.js-powered visual representations of attendance over time, helping identify patterns of absenteeism easily.
*   **Bulk Operations**: Select multiple students to apply bulk attendance statuses.

---

## 5. Reporting & Exports

Export data securely in various formats for offline analysis.

*   **Standard Reports**: Pre-configured exports for common operational needs (e.g., Monthly Attendance, Current Enrollment).
*   **Background Exports**: Large reports are generated asynchronously. You will receive a **Firebase Push Notification** when your file (CSV or XLSX) is ready to download, meaning you can continue working while the report processes.
*   **Analytics Dashboard**: Interactive charts visualizing age distribution, enrollment trends, and gender breakdowns.