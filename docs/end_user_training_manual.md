# BMA — NFE Sector Platform: End User Training Curriculum

**Revision: September 2026**

This is a **trainer's document**: an outline for running onboarding sessions with new users. It is
deliberately short and does not restate the product reference.

> **The reference manual is [`docs/wiki/end_user.md`](./wiki/end_user.md)**, which is also served inside
> the application at **Documentation → End User Manual** (`/dashboard/guide/end_user/`). Point trainees
> there for step-by-step instructions, field-by-field tables, the FAQ and troubleshooting.
>
> Earlier revisions of this file duplicated large parts of that manual. The duplicate has been removed so
> the two cannot drift apart — everything procedural now lives in one place.

---

## 1. Before the session

| Prerequisite | Detail |
|---|---|
| Accounts created | One account per trainee — never a shared login. Created in the Django admin by an administrator. |
| Groups assigned | Each account needs the group for its module (`MSCC`, `MSCC_CENTER`, `ALP_SCHOOL`, `CLM_Bridging`, …). See [`ACCESS_CONTROL.md`](./ACCESS_CONTROL.md). |
| Scope assigned | Each account also needs its **center**, **partner** or **school**. An account with a group but no assignment sees empty lists — this is the single most common "the system is broken" report. |
| Training data | Agree in advance whether trainees practise on a staging environment or on real records. Do not use real beneficiary data for practice entries in production. |
| Browser | Chrome or Firefox, notifications allowed for the site so export notifications can be demonstrated. |
| Language | Decide whether the session runs in English or Arabic; the interface supports both, with a right-to-left layout for Arabic. |

---

## 2. Session outline (all roles) — about 45 minutes

| # | Topic | Manual section |
|---|---|---|
| 1 | Logging in, password rules, the 30-minute inactivity logout, switching language | 1 |
| 2 | Reading the landing page: the metric cards, the trend chart, quick actions | 2 |
| 3 | Finding a person: quick search, the filtered list, sorting | 8 |
| 4 | Where to get help: the in-app manual, the escalation path | 24–25 |
| 5 | Data protection: no shared accounts, no exports on personal devices, log out when finished | 22 |

Close every session by having each trainee log in themselves, find one record, and open the in-app manual.

---

## 3. Role tracks

Run **one** of the following after the common session.

### 3.1 MSCC center staff — about 60 minutes

| # | Topic | Manual section |
|---|---|---|
| 1 | The 3-step registration wizard, and why the duplicate check matters | 3 |
| 2 | The child profile: Personal Info, Education situation, Attendances | 4 |
| 3 | Recording a service from the Education situation tab | 5 |
| 4 | Daily attendance, marking a day off, correcting a past day | 6 |
| 5 | Adding a teacher | 7 |
| 6 | Requesting an export and waiting for the notification | 9 |

### 3.2 ALP school focal points — about 60 minutes

| # | Topic | Manual section |
|---|---|---|
| 1 | The ALP home page and why you only ever see your own school | 12 |
| 2 | Registering a student, including the required child-labour question and the consent-form upload | 12 |
| 3 | Teacher records: assignment, subjects, levels, training, attachments | 12 |
| 4 | Student attendance: date, academic year, programme, absence reasons, day off | 12 |
| 5 | Downloading the day's attendance and opening it in Excel with Arabic names intact | 12 |
| 6 | Bulk teacher attendance | 12 |
| 7 | Entering grades, and what to do when a subject is missing | 12, 18 |
| 8 | Keeping the school profile and its map coordinates current | 12 |
| 9 | The five ALP dashboards | 12 |

### 3.3 Coordinators and management — about 45 minutes

| # | Topic | Manual section |
|---|---|---|
| 1 | Dashboards and how to filter them | 10 |
| 2 | Analytics, pivot tables, maps and the advanced exporter | 10 |
| 3 | Attendance heatmaps as a dropout-risk signal | 6 |
| 4 | Exports: field selection, XLSX vs CSV, why large exports run in the background | 9 |
| 5 | Reading the data critically — what filters were applied before this number was produced | 21 |

### 3.4 CLM bridging staff — about 45 minutes

| # | Topic | Manual section |
|---|---|---|
| 1 | Enrolling a student into a cycle | 11 |
| 2 | Pre-test and post-test assessments | 11 |
| 3 | Class-level attendance | 11 |
| 4 | Health visits, clubs, meetings, community initiatives and follow-ups, where the role allows | 11 |

---

## 4. Hands-on exercises

Give each trainee a worksheet with these tasks. They are deliberately ordered so that a mistake in one
step is visible in the next.

1. Log in and change your password.
2. Switch the interface to Arabic, then back.
3. Search for a beneficiary by name; then by ID number.
4. Register one practice beneficiary end to end. Deliberately re-enter the same name and date of birth a
   second time and observe the duplicate warning.
5. Open the beneficiary's profile and correct a deliberately misspelled name.
6. Record one service (MSCC) or one grade (ALP) for that beneficiary.
7. Take attendance for today, then reopen yesterday and correct one entry.
8. Request an export with a narrow date range and wait for the notification.
9. Open the End User Manual from the sidebar and find the FAQ answer for "I can't see the Export button".

---

## 5. Common misunderstandings to pre-empt

| Trainees often assume | The reality |
|---|---|
| "I can reset my own password." | There is no self-service reset link on the login page. An administrator resets it. |
| "Empty list means there is no data." | Far more often it means a filter is set, or the account has no center/school assigned. |
| "I can enter attendance for next week." | Future dates are rejected. Past dates can always be corrected. |
| "Deleting a record removes it." | Records are soft-deleted and remain in the database; only an administrator can act further. |
| "Administrators can fix my ALP entry for me." | Administrators are read-only in ALP by design. Only the school can enter or change its own data. |
| "The export failed because nothing happened." | Large exports run in the background for several minutes. The download button appears even if the push notification is missed. |
| "Arabic names are broken in my CSV." | Open the file from Excel's *File → Open* dialog rather than importing it as text. |

---

## 6. After the session

- Confirm every trainee has logged in successfully at least once from their own device.
- Record who was trained, on which module, and on what date.
- Share the escalation path in writing: center coordinator or school focal point → partner admin →
  system administrator.
- Remind trainees that the manual is always available in the sidebar under **Documentation**, so they do
  not need to keep a copy of this curriculum.
