
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

---

## 7. Teachers — Adding & Managing

### 7.1 Adding a New Teacher
1. Go to **MSCC → Teachers**.
2. Click **Add Teacher**.
3. Fill in the teacher's details (Name, Phone, Center).
4. Click **Save**.

### 7.2 Removing a Teacher
Click **Delete** next to the teacher's name. You will be asked to confirm. Deleted teachers cannot be assigned to new attendance sessions.

---

## 8. Searching for a Child

### 8.1 Quick Search (from any page)
A search bar is available in the navigation area. Type the child's:
- First name
- Last name
- ID number

Results appear as you type. Click on a result to go directly to the child's profile.

### 8.2 Full List with Filters
Go to **MSCC → Registrations List**. You will see all children registered at your center/partner.

Use the **filter bar** at the top to narrow results:
- **Status**: Active / Inactive / Deleted
- **Centre**: Filter by center (for partner-level users)
- **Round**: Filter by program round
- **Programme Type**: Filter by MSCC programme stream
- **Date Range**: Registration date range

You can also use the **search box** in the list to search by name or ID number within the filtered results.

### 8.3 Sorting the List
Click any column header to sort by that column. Click again to reverse the sort order.

---

## 9. Exporting Data

### 9.1 How to Request an Export
1. Go to **MSCC → Registrations List**.
2. Apply any filters you want (date range, center, round, etc.).
3. Click **Export** at the top of the list.
4. A dialog box opens. Select the **fields** you want to include in the export (or leave all selected for full data).
5. Choose the **format**: XLSX (Excel) or CSV.
6. Click **Generate Export**.

### 9.2 What Happens Next
Large exports are processed in the background. You will see:
```
Export requested. Processing... [spinner]
```

You can **continue using the system** while the export is being prepared. When it is ready:
- The button changes to **Download**.
- You will receive a **push notification** in your browser (if notifications are enabled) saying "Your export is ready."

Click **Download** to save the file to your computer.

### 9.3 Enabling Browser Notifications
To receive push notifications when exports are ready:
1. When the browser asks "Allow notifications from this site?" — click **Allow**.
2. If you missed this prompt, go to your browser settings → Notifications → find the site URL → set to **Allow**.

### 9.4 Export File Formats

| Format | Best for |
|---|---|
| **XLSX (Excel)** | Opening in Microsoft Excel or Google Sheets for analysis |
| **CSV** | Importing into other databases or tools |

> **Note:** Export access may be restricted to users with the **EXPORT** role. If you do not see the Export button, contact your coordinator.

---

## 10. Dashboards & Reports

### 10.1 MSCC Dashboard
Go to **MSCC → Dashboard**. This shows:

| Widget | Description |
|---|---|
| **Total Registrations** | Count of active registrations in the current round |
| **By Gender** | Pie chart — Male / Female breakdown |
| **By Nationality** | Chart of nationalities represented |
| **By Age Group** | Distribution of child ages |
| **Monthly Registrations** | Bar chart of new registrations per month |
| **Services Delivered** | Count of each service type delivered this round |
| **Attendance Rate** | Average attendance rate across all children |

### 10.2 Filtering the Dashboard
Use the filter controls at the top of the dashboard to narrow the data by:
- **Round** (program year)
- **Partner** (your organization)
- **Center**
- **Date range**

### 10.3 Wellbeing Dashboard
Go to **MSCC → Wellbeing Dashboard** for wellbeing-specific indicators including PSS session counts, referral rates, and follow-up completion rates.

### 10.4 Teacher Dashboard
Go to **MSCC → Teacher Dashboard** to see:
- Number of sessions delivered per teacher
- Teacher attendance
- Session frequency by subject/activity

### 10.5 Custom Dashboard
Go to **MSCC → Custom Dashboard** to build a view with your preferred indicators.

---

## 11. CLM Bridging Program

The CLM module manages students enrolled in **bridging / non-formal education** classes.

### 11.1 Enrolling a Student (CLM)
1. Go to **CLM → Students → Enroll New Student**.
2. Fill in the student's personal information (similar to MSCC registration).
3. Select the **Cycle** (program term) and **Center**.
4. Assign a **Teacher**.
5. Click **Save**.

### 11.2 CLM Student Status
Each CLM student moves through statuses:

| Status | Meaning |
|---|---|
| **Enrolled** | Student is actively participating |
| **Pre-Test** | Initial assessment has been administered |
| **Post-Test** | End-of-cycle assessment has been completed |

To update the status, open the student's profile and click the status button.

### 11.3 CLM Attendance
CLM attendance is recorded per class/session, not per individual center day.
1. Go to **CLM → Attendance**.
2. Select the **date**, **cycle**, and **class**.
3. Mark each student as present or absent.
4. Click **Save**.

### 11.4 CLM Assessments
Pre-test and post-test assessments are recorded from the student's profile page. Click **Add Pre-Test** or **Add Post-Test** and fill in the assessment scores.

---

## 12. Managing Your Account

### 12.1 Changing Your Password
1. Click your **username** in the top-right corner.
2. Select **Change Password**.
3. Enter your current password, then your new password twice.
4. Click **Save**.

Your new password must meet the same requirements as your original password (see [Section 1](#1-getting-started--login--navigation)).

### 12.2 Switching Language
1. Click your **username** in the top-right corner.
2. Select **English** or **العربية**.

The interface will reload immediately in the selected language.

### 12.3 Viewing Your Profile
1. Click your **username** → **Profile**.
2. You can see your assigned partner, center, and role groups.
3. Contact your system administrator to change any of these assignments.

---

## 13. Frequently Asked Questions (FAQ)

**Q: I can't find a child I registered last week. Where did they go?**
> Check the filter at the top of the Registrations List — it may be set to a different round or status. Set **Status** to "All" and clear any date filters, then search by name.

**Q: A child's name is spelled wrong. Can I fix it?**
> Yes. Open the child's profile → click **Edit** in the header → correct the name → click **Save**.

**Q: I accidentally marked the wrong child as present in attendance. Can I fix it?**
> Yes. Go to **Attendance**, find the date, and re-open the attendance session. Uncheck the child who was wrongly marked and save again. Attendance can be corrected for any past date.

**Q: The system says there is a duplicate when I register a new child. What do I do?**
> Review the potential duplicate carefully. If it is the **same child**, open their existing profile and do not create a new one. If it is a **different child** with a similar name and birth date, you can proceed with the new registration by confirming in the duplicate check dialog.

**Q: My export has been "processing" for a long time. What should I do?**
> Large exports can take 5–10 minutes. Leave the page open and wait for the push notification. If it has been more than 15 minutes, contact your system administrator who can check the export status.

**Q: I recorded services for the wrong child by mistake. What do I do?**
> Contact your system administrator — service records can be corrected or deleted from the admin panel. Do not try to work around this by creating duplicate entries.

**Q: The attendance heatmap is empty. Why?**
> The heatmap requires at least one attendance session to have been recorded. Make sure attendance has been saved at least once, then reload the page.

**Q: I can't see the Export button. Do I have access?**
> Export access is controlled by your user role. Contact your coordinator or system administrator to request the EXPORT permission if you need it.

**Q: I switched language to Arabic but some parts are still in English.**
> Some labels and dropdown options may not yet be translated. This is a known limitation. The core data entry fields are translated.

**Q: Can two people use the same account at the same time?**
> No. Each account should be used by one person only. Sharing accounts is against policy and makes the audit trail unreliable. Each staff member should have their own username.
