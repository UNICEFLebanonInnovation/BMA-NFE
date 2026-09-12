# End User Manual — BMA NFE Sector Platform

**Revision: September 2026 | UNICEF Lebanon NFE Sector**

This manual is written for field staff, center coordinators, school focal points, teachers, and partner organization staff who use the system day-to-day. No technical knowledge is required. Read each section that matches your role and refer back whenever needed.

The platform covers four operational modules. You will only see the ones your account is entitled to:

| Module | Who uses it | What it covers |
|---|---|---|
| **MSCC (Makani)** | Center staff, partners, UNICEF | Child registration, service delivery, attendance, dashboards |
| **ALP** | Public school focal points | Accelerated Learning Programme registration, teachers, attendance, grading |
| **CLM** | Bridging programme staff | Community Learning / bridging classes, assessments, follow-ups |
| **Reports & Analytics** | Coordinators and management | Dashboards, pivot tables, maps, exports |

---

## Table of Contents

1. [Getting Started — Login & Navigation](#1-getting-started-login-navigation)
2. [Your Dashboard](#2-your-dashboard)
3. [Registering a New Child (MSCC)](#3-registering-a-new-child-mscc)
4. [The Child Profile Page](#4-the-child-profile-page)
5. [Recording Service Delivery](#5-recording-service-delivery)
6. [Attendance — Recording & Viewing](#6-attendance-recording-viewing)
7. [Teachers — Adding & Managing](#7-teachers-adding-managing)
8. [Searching for a Child](#8-searching-for-a-child)
9. [Exporting Data](#9-exporting-data)
10. [Dashboards & Reports](#10-dashboards-reports)
11. [CLM Bridging Program](#11-clm-bridging-program)
12. [ALP — Accelerated Learning Programme](#12-alp-accelerated-learning-programme)
13. [Managing Your Account](#13-managing-your-account)
14. [Frequently Asked Questions (FAQ)](#14-frequently-asked-questions-faq)
15. [Troubleshooting Common Problems](#15-troubleshooting-common-problems)
16. [System Purpose](#16-system-purpose)
17. [User Roles and Access Levels](#17-user-roles-and-access-levels)
18. [Grading and Assessment Module](#18-grading-and-assessment-module)
19. [Headcount and Emergency Features](#19-headcount-and-emergency-features)
20. [Validation Rules and Common Restrictions](#20-validation-rules-and-common-restrictions)
21. [Best Practices for Users](#21-best-practices-for-users)
22. [Security and Data Protection Guidelines](#22-security-and-data-protection-guidelines)
23. [Glossary of Common Terms](#23-glossary-of-common-terms)
24. [Support and Escalation Process](#24-support-and-escalation-process)
25. [Getting Help](#25-getting-help)

---

## 1. Getting Started — Login & Navigation

### How to Log In

- Open your web browser (Chrome or Firefox recommended).
- Go to the system URL provided by your coordinator.
- Enter your **Username** and **Password**.
- Click **Sign In**.

> Accounts are created for you by an administrator. There is no self-service password reset — if you forget your password, contact your system administrator.

### Your First Login

On your first login you may be asked to change your password. Your password must:

| Rule | Requirement |
|---|---|
| Length | At least **8 characters** |
| Digits | At least **3 numbers** (0–9) |
| Uppercase | At least one letter **A–Z** |
| Lowercase | At least one letter **a–z** |
| Symbol | At least one of `( ) [ ] { } \| \` ~ ! @ # $ % ^ & * _ - + = ; : ' " , < > . / ?` |
| Not common | The password must not be a commonly used or all-numeric password, and must not look like your username |

### Automatic Logout

For security, the system **automatically logs you out after 30 minutes of inactivity**. Always save your work before stepping away.

### Failed Login Attempts

To protect accounts, repeated failed logins are rate limited. After **5 failed attempts within 5 minutes** the system stops accepting further attempts from that account for a short period. Wait a few minutes and try again, or ask your administrator to reset your password.

### The Navigation Bar and Sidebar

After logging in you will see a top bar and a left sidebar. The exact entries depend on your role:

| Area | What it gives you |
|---|---|
| **MSCC** | Child registrations, service delivery, teachers, MSCC attendance |
| **ALP** | ALP registrations, teachers, attendance, grading, school profile (ALP school users only) |
| **CLM** | Bridging registrations, assessments, clubs, meetings, follow-ups |
| **Attendance** | Record and view daily attendance |
| **Reports / Dashboards** | Charts, analytics, pivot tables, maps, downloads |
| **Documentation** | This manual, plus technical guides for administrators |
| **Username (top right)** | Change language, change password, view profile, log out |

### Switching Language

Click your **username** in the top-right corner → select **English** or **العربية** (Arabic). The page reloads in the selected language, with a full right-to-left (RTL) layout for Arabic.

### Finding This Manual Inside the System

This manual is available from the sidebar under **Documentation → End User Manual**. Administrators (superusers) also see additional technical guides in the same menu; standard users only see this manual.

---

## 2. Your Dashboard

When you log in, you land on the **Landing Page** — your home screen. ALP school users land on the ALP overview instead (see [Section 12](#12-alp-accelerated-learning-programme)).

### What You See

| Card | Description |
|---|---|
| **Today** | Registrations created today |
| **This Week** | New registrations over the last 7 days |
| **Centers / Schools reporting** | Sites that submitted data in the last 30 days |
| **Attendance** | Average attendance rate for the current month |
| **Registrations Trend** | Chart of new registrations over the last 14 days |
| **Recent Activity** | The last records added or modified |

### Quick Action Buttons

| Button | What it does |
|---|---|
| **New Registration** | Opens the registration form for your module |
| **Beneficiary List** | Opens the searchable list of registered children |
| **Track Attendance** | Opens the attendance entry page |
| **Export Data** | Opens the data export screen |

> **Tip:** The dashboard only shows data that belongs to your assigned center, partner, or school. You will not see records from other organizations.

---

## 3. Registering a New Child (MSCC)

Registration is done through a **3-step wizard**. You must complete all steps before the record is saved.

### Before You Start

Check if the child is **already registered** to avoid duplicates:

1. Use the **Quick Search** bar at the top of the registration list.
2. Search by first name + last name, or by ID number.
3. If the child is found → open their existing profile instead of creating a new one.

### Step 1 — Child Identity

Fill in the child's personal information:

| Field | Guidance |
|---|---|
| First Name | As written on the official document |
| Father's Name | Required |
| Last Name (Family Name) | Required |
| Mother's Full Name | Required |
| Gender | Select Male or Female |
| Date of Birth | Enter year, month, and day separately |
| Nationality | Select from the dropdown list |
| ID Type | UNHCR card, Lebanese ID, passport, birth certificate, etc. |
| ID Number | The number on the selected document |

**Duplicate Check:** As you type the child's name and date of birth, the system automatically searches for similar records. If a potential match appears, **review it carefully** before continuing. If it is the same child, open their existing profile instead.

Click **Next** to proceed to Step 2.

### Step 2 — Household & Social Info

| Field | Guidance |
|---|---|
| Caregiver | Who the child lives with (father, mother, relative, etc.) |
| Marital Status | For youth participants |
| Living Arrangement | Type of shelter/housing |
| Phone Number | Contact number for the family |
| Phone Owner | Who owns the phone (caregiver, child, other) |
| Disability | Yes/No — if yes, select the type |
| P-Code | Geographic code for the area (ask your coordinator if unsure) |
| Programme Type | Which MSCC program stream this child is enrolling in |
| Center | Your assigned center (usually pre-filled) |
| Partner | Your organization (usually pre-filled) |
| Round | The current program round (usually pre-filled) |
| Packages | Tick which service packages this child will receive (Education, Youth, Health & Nutrition, Child Protection, Social Protection) |

Click **Next** to proceed to Step 3.

### Step 3 — Review & Submit

Review all the information you entered:

- Check names are spelled correctly.
- Verify the date of birth.
- Confirm the ID number matches the physical document.

If anything is wrong, click **Back** to correct it.

When everything is correct, click **Submit Registration**.

A confirmation message appears and you are taken to the child's **Profile Page**.

> **Note:** If your internet connection drops during registration, the form data is saved in your browser. When you reconnect, your progress will still be there.

---

## 4. The Child Profile Page

The Profile Page is the **central record** for each registered child. Every service, assessment, and attendance record is accessible from here.

### Profile Header

At the top of the page you will see:

| Item | Description |
|---|---|
| Full Name | Child's registered name |
| ID | Document type and number |
| Status | Active / Inactive |
| Center | Where the child is registered |
| Partner | The organization responsible |
| Round | Current program round |
| Registered On | Date of registration |

Action buttons in the header:

- **Edit Profile** — Modify the child's demographic and household information.
- **New Round** — Register the same child into another programme round. A dialog shows the child's
  registration history and the rounds still available; if the child is already registered in every
  round, the dialog says so instead.

> Cancelling or deleting a registration is not exposed as a button in the interface. Ask your system
> administrator if a record has to be cancelled or removed.

### Profile Tabs

| Tab | Contents |
|---|---|
| Personal Info | Full demographic, identity and household information |
| Education situation | Education history and every service delivery record (education, health, youth, PSS, inclusion, digital, recreational, LEGO, referrals, follow-ups) |
| Attendances | Attendance history with a month-by-month calendar view |

---

## 5. Recording Service Delivery

Service delivery is recorded from the child's **Profile Page → Education situation tab**, where the
services table sits under the education history.

Each service type has its own form. Click the **+ Add** button next to the relevant service.

### Education Services

#### Education Assessment (Baseline)

Records the child's reading and numeracy levels at the start of the program.

| Field | Description |
|---|---|
| Assessment Date | Date the assessment was conducted |
| Reading Level | Select from the scale |
| Numeracy Level | Select from the scale |
| Grade Level | Child's current or equivalent grade |

#### Diagnostic Assessment

A more detailed subject-by-subject assessment.

#### Education Service (Sessions)

Records that education sessions were delivered.

| Field | Description |
|---|---|
| Session Date | Date of the session |
| Number of Sessions | How many sessions in this entry |
| Programme Type | Which education programme |
| Enrollment Count | Number of children enrolled for the entry |

#### Education Grading

End-of-cycle grades/results.

#### School Grading

Grades reported by the formal school the child attends.

#### Remedial Support (RS)

Additional tutoring or support sessions provided.

---

### Health & Nutrition

#### Health/Nutrition Check

Records a health screening for the child.

| Field | Description |
|---|---|
| Date | Date of the check |
| Weight (kg) | Child's weight |
| Height (cm) | Child's height |
| MUAC | Mid-upper arm circumference (for under-5 children) |
| Vaccination Status | Up to date / Not up to date |
| Referral Needed | Yes/No |

#### Health Referral

Records a referral to an external health service.

| Field | Description |
|---|---|
| Referral Date | Date the referral was made |
| Referred To | Organization or clinic |
| Reason | Brief description |

---

### Youth Services

#### Youth Assessment

Baseline assessment for youth participants.

#### Youth Kit

Records distribution of a youth materials kit.

#### Maharati (Vocational Training)

Records Maharati vocational skill-building sessions.

| Field | Description |
|---|---|
| Session Date | Date of the session |
| Module | Which Maharati module |
| Sessions Completed | Number |

#### GIL (Girls' Improved Learning)

Records GIL sessions delivered to youth participants.

#### Youth Referral

Records a referral of a youth participant to another service or programme.

#### Youth Scoring

End-of-cycle outcome scoring for youth participants.

---

### Psychosocial Support (PSS)

Records PSS group or individual sessions.

| Field | Description |
|---|---|
| Session Date | Date of the session |
| Session Type | Group / Individual |
| Number of Sessions | Count for this entry |
| Facilitator | Staff name |

---

### Inclusion Services

Records sessions for children with disabilities or special needs.

---

### Digital Skills

Records digital literacy training sessions.

| Field | Description |
|---|---|
| Session Date | Date of the session |
| Module | Topic covered |
| Sessions Completed | Count for this entry |

---

### Recreational Activities

Records recreational or sport sessions.

---

### LEGO Therapy

Records LEGO-based therapeutic play sessions (typically for younger children).

| Field | Description |
|---|---|
| Session Date | Date of the session |
| Age Group | Selected automatically based on child's age |
| Sessions | Number of sessions |

---

### Referrals & Follow-ups

#### Referral

Records a cross-program or external service referral.

| Field | Description |
|---|---|
| Referral Date | Date the referral was made |
| Referred To | Program or organization |
| Type | Internal / External |
| Reason | Why the child was referred |

#### Follow-up

Records a case follow-up visit or call.

| Field | Description |
|---|---|
| Follow-up Date | Date of the follow-up |
| Method | Visit / Phone call |
| Notes | What was discussed or observed |

---

### Saving Service Records

All service forms are submitted directly from the child profile page. After clicking **Save**:

- The form closes automatically.
- The new record appears in the services table immediately.
- You do **not** need to reload the page.

If there is an error (e.g., a required field is missing), a red error message appears on the field that needs to be fixed.

---

## 6. Attendance — Recording & Viewing

### Recording Daily Attendance

- Click **Attendance** in the navigation, or go to **MSCC → Attendance**.
- The system defaults to **today's date** and your assigned center.
- The list of all active children registered at your center appears.
- For each child, tick ✓ **Present** or leave blank for **Absent**.
- You can also use **Select All Present** for a quick full-class entry.
- If the center did not open that day, mark it as a **day off** and give the reason instead of marking children individually.
- Click **Save Attendance** when done.

> **Important:** You can only record attendance for the **current day** or days in the past. Future dates are not allowed.

**Tip:** If a child is not appearing in the attendance list, check that their registration is **Active** in their profile.

### Viewing a Child's Attendance

From the child's **Profile Page → Attendances tab**:

- A calendar shows green (present) and red/empty (absent) days.
- Below the calendar is a full list of attendance records.
- The attendance percentage is shown at the top.

### Attendance Heatmap

Go to **Attendance → Heatmap** to see a visual grid of attendance across all children and all days in the program round. This helps identify:

- Children with consistently low attendance (possible dropout risk)
- Days with unusually low overall attendance

Colors in the heatmap:

| Color | Meaning |
|---|---|
| Dark green | High attendance rate |
| Light green / Yellow | Moderate attendance |
| Red / Empty | Low or no attendance |

### Attendance Report

Go to **Attendance → Report** for a summary table showing:

- Total days per child
- Days present
- Days absent
- Attendance percentage

This report can be exported to Excel (see [Section 9](#9-exporting-data)).

---

## 7. Teachers — Adding & Managing

Teachers and facilitators working at your center must be registered in the system.

### Adding a Teacher

- Go to **MSCC → Teachers → Add Teacher**.
- Fill in the form:

| Field | Guidance |
|---|---|
| First Name | As written on the official document |
| Father's Name | Required |
| Last Name | Required |
| Gender | Male / Female |
| Nationality | Select from the list |
| ID Type | Type of identity document |
| ID Number | Number on the document |
| Partner | Your organization (usually pre-filled) |
| Center | The center where this teacher works |

- Click **Save**.

### Editing a Teacher

- Go to **MSCC → Teachers**.
- Find the teacher in the list.
- Click **Edit** next to their name.
- Make changes and click **Save**.

### Removing a Teacher

Click **Delete** next to the teacher's name. You will be asked to confirm. Deleted teachers cannot be assigned to new attendance sessions.

---

## 8. Searching for a Child

### Quick Search (from any page)

A search bar is available in the navigation area. Type the child's:

- First name
- Last name
- ID number

Results appear as you type. Click on a result to go directly to the child's profile.

### Full List with Filters

Go to **MSCC → Registrations List**. You will see all children registered at your center/partner.

Use the **filter bar** at the top to narrow results:

| Filter | What it does |
|---|---|
| Status | Active / Inactive / Deleted |
| Centre | Filter by center (for partner-level users) |
| Round | Filter by program round |
| Programme Type | Filter by MSCC programme stream |
| Date Range | Registration date range |

You can also use the **search box** in the list to search by name or ID number within the filtered results.

### Sorting the List

Click any column header to sort by that column. Click again to reverse the sort order.

---

## 9. Exporting Data

### How to Request an Export

- Go to **MSCC → Registrations List**.
- Apply any filters you want (date range, center, round, etc.).
- Click **Export** at the top of the list.
- A dialog box opens. Select the **fields** you want to include in the export (or leave all selected for full data).
- Choose the **format**: XLSX (Excel) or CSV.
- Click **Generate Export**.

### What Happens Next

Large exports are processed in the background. You will see:

```
Export requested. Processing... [spinner]
```

You can **continue using the system** while the export is being prepared. When it is ready:

- The button changes to **Download**.
- You will receive a **push notification** in your browser (if notifications are enabled) saying "Your export is ready."

Click **Download** to save the file to your computer.

### Enabling Browser Notifications

To receive push notifications when exports are ready:

1. When the browser asks "Allow notifications from this site?" — click **Allow**.
2. If you missed this prompt, go to your browser settings → Notifications → find the site URL → set to **Allow**.

### Export File Formats

| Format | Best for |
|---|---|
| XLSX (Excel) | Opening in Microsoft Excel or Google Sheets for analysis |
| CSV | Importing into other databases or tools |

> **Arabic text in CSV:** CSV exports are written in UTF-8 with a byte-order mark so that Arabic names display correctly when the file is opened directly in Excel.

> **Note:** Export access may be restricted to users with the **EXPORT** role. If you do not see the Export button, contact your coordinator.

---

## 10. Dashboards & Reports

### MSCC Dashboard

Go to **MSCC → Dashboard**. This shows:

| Indicator | Description |
|---|---|
| Total Registrations | Count of active registrations in the current round |
| By Gender | Pie chart — Male / Female breakdown |
| By Nationality | Chart of nationalities represented |
| By Age Group | Distribution of child ages |
| Monthly Registrations | Bar chart of new registrations per month |
| Services Delivered | Count of each service type delivered this round |
| Attendance Rate | Average attendance rate across all children |

### Filtering the Dashboard

Use the filter controls at the top of the dashboard to narrow the data by:

- **Round** (program year)
- **Partner** (your organization)
- **Center**
- **Date range**

### Wellbeing Dashboard

Go to **MSCC → Wellbeing Dashboard** for wellbeing-specific indicators including PSS session counts, referral rates, and follow-up completion rates. Clicking an indicator drills down to the list of children behind the number.

### Teacher Dashboard

Go to **MSCC → Teacher Dashboard** to see:

- Number of sessions delivered per teacher
- Teacher attendance
- Session frequency by subject/activity

### Custom Dashboard

Go to **MSCC → Custom Dashboard** to build a view with your preferred indicators.

### Analytics, Pivot Tables and Maps

Under **Reports** you will also find:

| Report | What it does |
|---|---|
| Advanced Analytics | Trend, breakdown, and cross-tab views with filters for date, partner, center, programme, nationality, gender and age |
| Pivot Dashboard | Build your own cross-tabulations and drag dimensions into rows/columns |
| Chart Builder | Create a chart from selected indicators |
| Centers Map | Map of centers with registration counts per location |
| Advanced Exporter | Queue a large, fully customized export in the background |

---

## 11. CLM Bridging Program

The CLM module manages students enrolled in **bridging / non-formal education** classes.

### Enrolling a Student (CLM)

- Go to **CLM → Students → Enroll New Student**.
- Fill in the student's personal information (similar to MSCC registration).
- Select the **Cycle** (program term) and **Center**.
- Assign a **Teacher**.
- Click **Save**.

### CLM Student Status

Each CLM student moves through statuses:

| Status | Meaning |
|---|---|
| Enrolled | Student is actively participating |
| Pre-Test | Initial assessment has been administered |
| Post-Test | End-of-cycle assessment has been completed |

To update the status, open the student's profile and click the status button.

### CLM Attendance

CLM attendance is recorded per class/session, not per individual center day.

- Go to **CLM → Attendance**.
- Select the **date**, **cycle**, and **class**.
- Mark each student as present or absent.
- Click **Save**.

### CLM Assessments

Pre-test and post-test assessments are recorded from the student's profile page. Click **Add Pre-Test** or **Add Post-Test** and fill in the assessment scores.

### Other CLM Records

Depending on your role you may also have access to health visits, community initiatives, clubs, meetings, mid/post assessments and follow-up forms from the CLM menu.

---

## 12. ALP — Accelerated Learning Programme

The **ALP** module is used by public schools running the Accelerated Learning Programme. It is separate from MSCC: ALP records belong to a **school**, not to a center or partner.

### Who Can Use It

- Your account must be in the **ALP_SCHOOL** group and must be **linked to one school**.
- You can only see and edit data for **your own school**. Records from other schools are never shown.
- If your account has no school assigned, ALP pages will load but the lists stay empty and a warning is shown. Ask your administrator to link your account to a school.
- Site administrators (superusers) who are given ALP access can **view** ALP data, but the add/edit/delete screens are deliberately blocked for them — data entry is the school's responsibility.

### The ALP Home Page

ALP users are taken straight to the **ALP overview** after login (rather than the general landing page). It shows:

| Card | Description |
|---|---|
| Today | Registrations created today |
| This Week | New registrations over the last 7 days |
| Schools | Schools reporting data |
| Attendance | Average attendance for the current month |
| Registrations Trend | Chart of the last 14 days |

Quick actions take you to **New Registration**, **Beneficiary List**, and **Track Attendance**.

### Registering a Student (ALP)

Go to **ALP → Registrations → Add**. The form follows the same child identity, caregiver and ID workflow as MSCC, plus ALP-specific fields:

| Field | Guidance |
|---|---|
| Academic year (Round) | Only the current academic year is selectable |
| Programme | The ALP programme/level the student joins |
| Registration date | Date the student was registered |
| Source of identification | How the student was referred to ALP (ALP-specific list, including the BLN programme and NFE referrals) |
| Child labour | Whether the child works — **required**. Follow-up questions (type, hours, weekly income, working conditions) only appear when the answer is *Yes* |
| Cash support programmes | Any cash assistance the household receives |
| Packages | Service packages the student will receive |
| Consent form copy/photo | Upload a scanned copy or clear photo of the signed consent form (PDF or image) |
| Child photo | Optional photo of the student |

> The **school** is not shown on the form — it is set automatically from the school linked to your account.

**Duplicate check:** as with MSCC, the system checks for an existing child with a similar name and date of birth while you type. Review any match carefully before continuing.

After saving, you are taken to the student's **ALP child profile**, which mirrors the MSCC profile layout.

### Managing the Registration List

Go to **ALP → Registrations**. The list is filtered to your school and offers:

- Filters (academic year, programme, status, date range)
- Column sorting
- **Edit** and **Delete** actions in the first column of each row
- **Export** to Excel/CSV — CSV exports are UTF-8 with a byte-order mark so Arabic names open correctly in Excel

### Teachers (ALP)

Go to **ALP → Teachers**. Teacher records capture the profile needed for ALP reporting:

| Field group | Contents |
|---|---|
| Identity | First / father's / last name, mother's full name, sex, date of birth, nationality, ID type and number |
| Assignment | Academic year, school, teacher assignment (and "other" description), subjects provided, registration levels taught |
| Workload | Teaching hours in the private school, teaching hours in MSCC, years of experience |
| Training | Trainings attended, number of sessions, date of completion, extra coaching and details |
| Attachments | Up to five supporting documents, each with a short description and a document type |

The school field is restricted to your own school. Use **Add**, **Edit** and **Delete** in the teacher list to manage records.

### Student Attendance (ALP)

Go to **ALP → Attendance**.

1. The **date** defaults to today. You can pick an earlier date; **future dates are rejected**.
2. Select the **academic year** and the **programme**.
3. The student list for your school loads automatically.
4. Mark each student **Attended / Not attended**. For an absence, choose the **absence reason** (and describe it if you select *Other*).
5. If the school was closed that day, set **Day off** to *Yes* and choose the **reason for closing** instead of marking students individually.
6. Click **Save**.

**Downloading the day's attendance:** click **Download** on the attendance page to get a CSV of exactly what is loaded on screen. The date, academic year and programme must all be selected first, otherwise the download is refused.

### Teacher Attendance (ALP)

Go to **ALP → Teacher Attendance** to record attendance for teachers in bulk:

- Pick the date, then mark each teacher's status.
- Save the whole list in one action.
- The list of past teacher attendance can be filtered and sorted.

### Grading (ALP)

Go to **ALP → Grading → Add**.

- Choose the **student registration** (restricted to your school).
- The system builds the grade fields automatically from the grading definitions configured by the administrator. Each definition has a **subject/material** and a **minimum and maximum grade**.
- Enter a value for each subject. Values outside the allowed range are rejected with a validation error.
- Click **Save**. Grades are stored against the registration and can be edited later.

> Because the grade fields come from configuration, the subject list can change between academic years without a software update. If a subject is missing, ask your administrator to add its grading definition.

### School Profile (ALP)

Go to **ALP → School Profile**. ALP focal points maintain their own school record:

| Section | Fields |
|---|---|
| School Information | School number, name, type, operating shift, director name, land phone number, email |
| Location | Governorate, district, cadaster, longitude, latitude |
| Provided Services | Provided packages, digital learning offered, digital hub available, number of administrative staff, nearby PHCC |

Click **Save changes** when done. Keeping the location coordinates accurate matters — they drive the school map on the dashboards.

### ALP Dashboards

| Dashboard | What it shows |
|---|---|
| **Registration** | Registration counts and trends, broken down by programme, gender, nationality and age |
| **Teacher** | Teacher counts, assignments, qualifications, workload and learning-outcome insights |
| **Attendance** | Attendance rates over time, in the same heatmap style as MSCC |
| **School** | Map of ALP schools with their registration and attendance figures |
| **Pivot** | Build your own cross-tabulation of ALP data; also open to site administrators for cross-school reporting |

All dashboards except the pivot are limited to your own school's data.

---

## 13. Managing Your Account

### Changing Your Password

- Click your **username** in the top-right corner.
- Select **Change Password**.
- Enter your current password, then your new password twice.
- Click **Save**.

Your new password must meet the same requirements as your original password (see [Section 1](#1-getting-started-login-navigation)).

### Switching Language

- Click your **username** in the top-right corner.
- Select **English** or **العربية**.

The interface will reload immediately in the selected language.

### Viewing Your Profile

- Click your **username** → **Profile**.
- You can see your assigned partner, center or school, and your role groups.
- Contact your system administrator to change any of these assignments.

---

## 14. Frequently Asked Questions (FAQ)

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

**Q: (ALP) My ALP lists are completely empty even though my school has students.**

> Your account is probably not linked to a school yet. ALP records are filtered strictly by the school on your user account. Ask your administrator to set your school.

**Q: (ALP) I am an administrator and the ALP "Add" button gives me a permission error.**

> That is intentional. Site administrators have read-only access to ALP; only school accounts may create or change ALP records.

**Q: (ALP) My Arabic names look like symbols when I open the attendance CSV in Excel.**

> Open the file directly from Excel's *File → Open* dialog rather than importing it as plain text. The export is UTF-8 with a byte-order mark, which Excel recognises automatically when the file is opened normally.

---

## 15. Troubleshooting Common Problems

### "This site can't be reached" / Page won't load

- Check your internet connection.
- Try refreshing the page (press **F5** or **Ctrl+R**).
- Try opening the URL in a different browser.
- If the problem persists, contact your coordinator — the server may be temporarily down.

### Page loads but shows a blank white screen

- Press **Ctrl+Shift+R** (hard refresh) to clear cached files.
- Try logging out and logging back in.
- Try a different browser.

### Login fails — "Invalid username or password"

- Check that **Caps Lock** is not on.
- Make sure you are using your **username**, not your email address.
- After 5 failed attempts in 5 minutes the system stops accepting further attempts for a short period. Wait a few minutes and try again.
- Contact your administrator to reset your password.

### Form won't submit — red error messages appear

Red messages appear next to fields that have problems:

| Message | What to do |
|---|---|
| "This field is required" | Fill in the empty field |
| "Enter a valid date" | Check the date format (day/month/year) |
| "ID number already exists" | Another record with this ID number already exists — check for duplicates |
| "Ensure this value is less than or equal to …" | The grade or number you entered is outside the allowed range |

### Export button is greyed out or not visible

Your account may not have the EXPORT role. Contact your system administrator.

### Push notifications not working

- Check that your browser allows notifications for this site (browser settings → Notifications).
- Make sure you are not in private/incognito mode — notifications are disabled in private mode.
- Try refreshing the page after the export is submitted — the download button should appear even without a notification.

### Attendance list is empty — no children showing

- Confirm you are selecting the correct **center/school**, **date**, **round** and **programme**.
- Check that the children are registered as **Active** in the Registrations List.
- Make sure the current program **Round / academic year** is set as active. Contact your administrator if unsure.
- For ALP, confirm your account is linked to a school.

### Session expired — redirected to login page

The system logged you out after 30 minutes of inactivity. Log back in. If you were filling a long form, the data may have been saved as a draft in your browser — check if the fields are still populated when you return to the form.

---

## 16. System Purpose

The BMA-NFE platform supports education and programme management operations for the Non-Formal Education sector. The system centralizes registration, attendance tracking, student monitoring, reporting, and educational workflows.

The system allows organizations to:

- Maintain accurate beneficiary records
- Track educational participation
- Monitor attendance and performance
- Generate operational reports
- Produce dashboards and statistics
- Export data for programme reporting
- Improve data quality and operational visibility

---

## 17. User Roles and Access Levels

Access is driven by the **groups** assigned to your account, combined with the **center**, **partner** or **school** it is linked to. Different users have different permissions depending on their role.

### Registration Officer

Registration Officers are responsible for:

- Creating beneficiary profiles
- Updating personal information
- Managing registration workflows
- Uploading attachments and documents

Typical access includes: Registration pages, Child profiles, Family information, Registration editing.

### Teacher

Teachers are responsible for:

- Taking attendance
- Recording grades
- Reviewing class lists
- Monitoring student progress

Typical access includes: Attendance pages, Grading pages, Student lists, Teacher dashboards.

### ALP School Focal Point

School-based users running the Accelerated Learning Programme. They register students, maintain teacher records, take student and teacher attendance, enter grades, and keep their school profile up to date — always limited to their own school.

### Programme Coordinator

Programme Coordinators manage programme operations. Responsibilities include:

- Reviewing reports
- Monitoring attendance
- Supervising registrations
- Tracking programme statistics

### Management Users

Management users usually have broader access to: Dashboards, Exports, Reports, Administrative modules.

### System Administrators

Administrators manage:

- User accounts, groups, and center/partner/school assignments
- System configurations, including programme rounds and grading definitions
- Data corrections
- Advanced troubleshooting

Administrators are also the only users who can read the technical guides inside the application.

> The exact group names used by the system and the views each one unlocks are listed in the [Access Control Matrix](../ACCESS_CONTROL.md).

---

## 18. Grading and Assessment Module

The grading module allows educational performance tracking for enrolled students.

### Entering Grades

- **Select Student** — Choose the Programme, Section, and then the Student. In ALP, choose the student's registration.
- **Enter Scores** — Assessment areas may include:

- Arabic
- English
- French
- Mathematics
- Social emotional learning
- Artistic performance

In ALP the list of subjects is not fixed in the software: it is generated from the grading definitions your administrator configures, each with its own minimum and maximum grade.

### Grade Validation

The system enforces minimum and maximum values per programme-specific thresholds. Invalid grades trigger validation errors.

> **Important:** Save entries carefully and double-check scores before submission. Invalid grades are blocked automatically.

---

## 19. Headcount and Emergency Features

Some implementations include headcount and emergency response features for safety and accountability.

### Headcount Process

Users can:

- Submit safety status
- Record current location information
- Provide emergency details

### Common Headcount Fields

| Field | Description |
|---|---|
| Safety Status | Indicate whether the person is safe |
| Current Location | Reported location at time of submission |
| GPS Coordinates | Precise location if available |
| Country | Country of current location |
| Additional Notes | Any relevant context or details |

> **Guideline:** Provide accurate information. Verify GPS data before submitting. Emergency responses should be updated promptly.

---

## 20. Validation Rules and Common Restrictions

The system includes multiple validation mechanisms to ensure data quality.

### Required Fields

Mandatory fields cannot be left empty. They are marked with a red asterisk (*).

### Date Restrictions

- Registration dates cannot be in the future
- Attendance cannot be recorded for a future date
- Attendance dates cannot precede registration dates
- Invalid date sequences are blocked automatically

### Duplicate Prevention

The system blocks or warns about:

- Duplicate registrations (the duplicate check runs while you type the child's name and date of birth)
- Duplicate attendance records for the same day
- Duplicate programme assignments

### Conditional Fields

Some fields only appear when certain options are selected. Examples:

- Selecting **"Other"** may reveal an additional specification field.
- Child labour follow-up questions only appear when child labour is reported.
- Sibling disability questions only appear when the child has siblings.
- Certain education statuses (e.g., Dropout) require a dropout date to be entered.

### File Uploads

- Consent forms and supporting documents accept PDF files and images.
- Upload a clear, readable scan or photo — unreadable uploads have to be replaced later.

---

## 21. Best Practices for Users

Users are encouraged to follow these practices to maintain data quality and system integrity:

- Save work regularly throughout a session
- Verify information before submission
- Use consistent naming conventions
- Avoid creating duplicate entries
- Review attendance carefully before saving
- Keep uploaded documents organized and clearly labelled
- Report technical issues to the administrator immediately
- Apply filters gradually and verify results before exporting
- Use smaller date ranges when generating exports when possible

---

## 22. Security and Data Protection Guidelines

Because the system contains sensitive beneficiary information, users must follow security practices at all times.

### Security Rules

- Keep credentials confidential — never share your password
- Avoid sharing accounts with other users
- Log out after each session
- Use secure and trusted devices when possible
- Avoid downloading sensitive data unnecessarily

### Data Protection

- Access only the information you are authorized to view
- Avoid storing exports on unsecured or personal devices
- Follow your organization's data protection policies

> **Reminder:** The system contains personal data of children and families, including uploaded consent forms and identity documents. Any misuse or unauthorized sharing of this data is a serious breach of policy.

---

## 23. Glossary of Common Terms

| Term | Meaning |
|---|---|
| ALP | Accelerated Learning Programme — a school-based catch-up programme |
| Attendance Record | A stored attendance entry for a student on a specific date |
| Beneficiary | A registered individual receiving programme services |
| Center | A physical location where programme activities are delivered |
| CLM | Community Learning / bridging educational programme |
| Dashboard | The main summary interface displaying statistics and navigation shortcuts |
| Export | A generated file (Excel or CSV) containing filtered system data |
| Focal point | The person at a center or school responsible for data entry |
| MSCC | Makani Social and Community Centres programme |
| P-Code | Standard geographic code identifying a Lebanese locality |
| Programme | An educational or operational activity offered at a center or school |
| Registration Officer | Staff responsible for creating and managing beneficiary profiles |
| Round | An operational or educational cycle (e.g., academic year or programme period) |
| Section | A class grouping within a programme |

---

## 24. Support and Escalation Process

If you encounter issues that cannot be resolved locally, follow this escalation path:

1. **Verify Inputs** — Check required fields, applied filters, and your internet connection.
2. **Retry** — Refresh the page, log out and log back in, then retry the operation.
3. **Contact Technical Team** — Provide:
   - A screenshot of the issue
   - Your user role
   - Steps to reproduce the problem
   - Date and time the issue occurred
   - Browser name and version
4. **Escalate to Administrator** — If the issue persists, escalate to the system administrator. Provide logs if requested and avoid repeated submissions during the investigation.

> **Tip:** Always include a screenshot when reporting an issue — it significantly speeds up diagnosis.

---

## 25. Getting Help

If you encounter a problem not covered in this manual:

- **Contact your Center Coordinator or School Focal Point** for day-to-day operational questions.
- **Contact your Partner Admin** for access and permission issues.
- **Contact the System Administrator (Ministry IT)** for technical problems, account resets, or data corrections.

Always include:

- Your **username**
- The **date and time** of the problem
- What you were trying to do
- A **screenshot** if possible

---

BMA — NFE Sector Platform · End User Manual · Revised September 2026

UNICEF Lebanon NFE Sector
