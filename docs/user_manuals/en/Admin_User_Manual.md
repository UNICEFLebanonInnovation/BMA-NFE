# Admin Panel – User Management and Permissions

**BMA Platform – Administrator Manual**

_Last updated: 26 October 2026_

This manual explains how to use the **administration panel** of the BMA platform. It focuses on **user management and permissions**: creating accounts, assigning roles and the center, partner or school each account may see, resetting passwords, deactivating accounts and understanding what every role can do. It also covers the reference tables the administrator maintains (partners, centers, schools, rounds, programmes) and the monitoring pages.

The administration panel is reserved for accounts with **staff status**. A **superuser** has every right; a staff account without superuser status only sees the pages it was explicitly granted (see section 10). Changes made here apply **immediately** to the field users, so always double-check before saving.

Each step is illustrated with a screenshot taken from the system. The data shown is demonstration data only.

## Contents

1. Accessing the Admin Panel
2. How Access Works
3. Center, Partner or School – Choosing the Assignment
4. The Users List
5. Creating an Account
6. Role Recipes
7. Modifying an Account
8. Resetting a Password
9. Deactivating, Reactivating and Deleting Accounts
10. Groups and Permissions
11. Reference Data
12. Monitoring
13. Good Practices
14. Frequently Asked Questions

## 1. Accessing the Admin Panel

Open the platform address followed by **/admin/** (for example `https://<platform>/admin/`). You can also open it from the user menu of the application, entry **Admin**, when your account has staff status.

1. Enter your **username** and **password** on the administration login page.

    ![Figure 1](../screenshots/en/adm_00_login_empty.png)

    *Figure 1 – Administration login page*

2. Click **Log in**. Only accounts with staff status are accepted; other accounts receive an error.

    ![Figure 2](../screenshots/en/adm_00_login_filled.png)

    *Figure 2 – Login form filled in*

3. The **Dashboard** lists every data table you may manage, grouped by area: NFE data, Attendances, Child data configuration, Schools, Locations, Users, Backends (monitoring), ALP and configuration. **Recent actions** on the right shows the last changes made by your account.

    ![Figure 3](../screenshots/en/adm_01_dashboard.png)

    *Figure 3 – The administration dashboard*

4. The **left menu** lists the same tables; the **top bar** gives quick access to Users, Schools and Locations. The icon at the top right opens the user menu: **See site** (back to the application), **Change password** and **Log out**.

    ![Figure 4](../screenshots/en/adm_02_user_menu.png)

    *Figure 4 – The user menu of the admin panel*


> **Note:** The admin panel follows the language chosen in the application (globe icon). The interface and most labels are translated; group names and technical identifiers are always shown as stored.

## 2. How Access Works

What a user can see and do is decided by **three things** on the user record. All three must be consistent, otherwise the user sees empty lists or a "permission denied" page.

| Setting | Where | Effect |
|---|---|---|
| **Status flags** | Permissions tab | **Active** allows login. **Staff status** opens the admin panel. **Superuser status** grants every right everywhere. |
| **Groups (roles)** | Permissions tab | Each group name unlocks a set of pages in the application: NFE, ALP or CLM pages, exports, sector-wide lists. |
| **Assignment** | Personal info tab | The **center**, **partner** or **school** linked to the account. Lists, dashboards and exports are filtered to it. |

The application checks the **group name** exactly as written. Create accounts with the existing groups below; do not rename them and do not create new ones unless the development team has added the matching code.

| Group name | What it gives |
|---|---|
| `MSCC` | NFE data entry: registrations, services, assessments, attendance of the assigned center |
| `MSCC_CENTER` | Limits the NFE lists to the center linked to the account. Combine with `MSCC` |
| `MSCC_PARTNER` | Read-oriented view over all the centers of the partner organisation linked to the account |
| `MSCC_FULL` | Removes the center/partner filter on the NFE beneficiary list (sector-wide view) |
| `MSCC_UNICEF` | Sector-wide analytics, reports and exports for UNICEF staff |
| `EXPORT` | Unlocks the export buttons on lists that gate them |
| `YOUTH` | Marks youth-stream accounts (used by the admin "User Category" filter) |
| `ALP_SCHOOL` | ALP school focal point. Required for every ALP page; data limited to the linked school |
| `CLM_Bridging`, `CLM_BRIDGING_ALL`, `CLM_ATTENDANCE`, `CLM_TEACHER`, `CLM_Inclusion` | Community Learning (bridging) module roles |

- A **center user** needs `MSCC` + `MSCC_CENTER`, a **center** and the **partner** that runs it. Add `EXPORT` if the user may download data.
- A **partner coordinator** needs `MSCC_PARTNER` and the **partner**; no center.
- An **ALP school focal point** needs `ALP_SCHOOL` and a **school**. Without the school every ALP list stays empty.
- A **UNICEF or ministry reader** needs `MSCC_UNICEF` (or `MSCC_FULL` with `MSCC_CENTER` for the sector-wide list); no assignment is required.
- Superusers can **view** ALP data but can **never add or edit** it: ALP data entry is reserved for the school accounts.
- The **User permissions** box (individual model permissions) does not affect the application; it only matters for staff accounts that use the admin panel without superuser status (section 10).

## 3. Center, Partner or School – Choosing the Assignment

The **Personal info** tab has three assignment fields: **Partner**, **Center** and **School**. Which ones you fill depends on the kind of account, and the groups must match. This is the most frequent source of "empty lists" and "permission denied" problems, so use the table below every time you create or modify an account.

| Account | Groups | Partner field | Center field | School field |
|---|---|---|---|---|
| Center data-entry user (works in one center) | `MSCC` + `MSCC_CENTER` | **Yes** – the partner that runs the center | **Yes** – the one center | empty |
| Partner coordinator (monitors all the centers of the organisation) | `MSCC_PARTNER` | **Yes** – the organisation | empty | empty |
| UNICEF / ministry reader (whole sector) | `MSCC_UNICEF` | empty | empty | empty |
| ALP school focal point | `ALP_SCHOOL` | empty | empty | **Yes** – the one school |
| Administrator | none (Staff + Superuser status) | empty | empty | empty |

Both roles belong to the NFE module, but they serve different people and give different rights:

|  | `MSCC_CENTER` (with `MSCC`) | `MSCC_PARTNER` |
|---|---|---|
| Who | A data-entry officer or facilitator working **in one center** | A coordinator or M&E officer of the **partner organisation** |
| Scope of data | Only the children, attendance and teachers of the **center** linked to the account | The children, attendance and teachers of **all the centers** of the **partner** linked to the account |
| Register children, record services, exams, attendance | **Yes** | **No** – read-only on registrations; can view and filter the lists |
| Manage teachers | Yes, for the center | Yes, for all the centers of the partner |
| Export beneficiary data | The center's registrations (with the `EXPORT` group where the list requires it) | All the partner's registrations |
| Dashboards and heatmaps | The center | All the centers of the partner |
| Required assignment | Center **and** Partner | Partner only |

- For every NFE account that belongs to an organisation: center users **and** partner coordinators.
- The partner is written on each registration the user creates, and it decides what a `MSCC_PARTNER` user can see.
- For a center user, choose the partner that **operates the center**. If the center is later moved to another partner, update the accounts of that center too.

- Only for accounts that **enter data in one specific center** (`MSCC` + `MSCC_CENTER`).
- The attendance page, the registration form and the beneficiary list are filtered to this center; a center user with no center sees a warning and empty lists.
- Never give a center to a `MSCC_PARTNER` coordinator: it is ignored for their lists and only causes confusion. A person who works in two centers needs two accounts, or a partner-level account if read access is enough.

- Only for **ALP** accounts (`ALP_SCHOOL`). The school is the equivalent of the center for the ALP module: registrations, attendance, teachers, grades and dashboards are limited to it.
- Leave Partner and Center empty on an ALP account; they have no effect on ALP pages.
- The field only offers schools that are not closed. If the school is missing, create or reopen it under **Schools** first (section 11).

> **Note:** Rule of thumb: **Center = enters data for one center**, **Partner = watches all the centers of an organisation**, **School = ALP focal point**. One account should fit exactly one line of the first table.

## 4. The Users List

Open **Users → Users** in the left menu (or the **Users** entry of the top bar).

1. The list shows the username, names, active flag, email, school, center, partner, phone and the **user category** (derived from the groups). Click a column header to sort. The **Add user** button creates an account; **Import** and **Export** exchange the user list as a file.

    ![Figure 5](../screenshots/en/adm_10_users_list.png)

    *Figure 5 – The users list*

2. Type a username, name or school in the search box and press **Search**.

    ![Figure 6](../screenshots/en/adm_11_users_search.png)

    *Figure 6 – Searching users*

3. Use the filter lists above the table (**groups**, **school**, **center**, **Partner**, **active**, **User Category**) to narrow the list, for example all the accounts of one center or every inactive account.

    ![Figure 7](../screenshots/en/adm_12_users_filtered.png)

    *Figure 7 – Users filtered by group*

4. **Export** downloads the list (CSV, XLSX, JSON…) with the names, assignments, active flag and category of each user. Use it for periodic access reviews.

    ![Figure 8](../screenshots/en/adm_14_users_export.png)

    *Figure 8 – Exporting the user list*

5. **Import** loads a file in the same layout to create or update many accounts at once. Always use **Preview** first and check the differences before confirming.

    ![Figure 9](../screenshots/en/adm_15_users_import.png)

    *Figure 9 – Importing users*


> **Note:** Passwords are never exported. Imported accounts have no usable password until you reset it (section 8).

## 5. Creating an Account

Creating an account takes two screens: first the username and password, then the personal information, assignment and roles.

1. Click **Add user**. Enter the **username** (letters, digits and @ . + - _ only; it cannot be changed easily later) and the **password** twice. Use the agreed naming convention, for example `firstname.lastname` or `center.city`.

    ![Figure 10](../screenshots/en/adm_20_add_user_empty.png)

    *Figure 10 – The Add user form*

2. Click **Save**. The account is created and the full user form opens with the message "was added successfully".

    ![Figure 11](../screenshots/en/adm_21_add_user_filled.png)

    *Figure 11 – Username and password filled in*

3. On the **Personal info** tab enter the first name, last name, email and phone, then the assignment: the **Partner** and **Center** for an NFE account, or the **School** for an ALP account (type part of the school name and pick it from the list).

    ![Figure 12](../screenshots/en/adm_23_add_user_personal_info.png)

    *Figure 12 – Personal info and assignment*

4. On the **Permissions** tab keep **Active** ticked. Tick **Staff status** only for administrators. In **Groups**, select the roles in the left box and move them to the right box with the arrow (double-click also works). Leave **User permissions** empty.

    ![Figure 13](../screenshots/en/adm_24_add_user_permissions.png)

    *Figure 13 – Groups chosen for a center data-entry account*

5. Click **Save**. The list reopens with a confirmation message. Give the credentials to the user through a secure channel and ask them to change the password at first login.

    ![Figure 14](../screenshots/en/adm_25_add_user_done.png)

    *Figure 14 – Account saved*


| Password rule | Requirement |
|---|---|
| Length | At least 8 characters |
| Digits | At least 3 digits |
| Letters | At least one upper-case and one lower-case letter |
| Symbol | At least one symbol such as ! @ # $ % & * |
| Not common | Not a common word and not similar to the username |

## 6. Role Recipes

Use these combinations when creating accounts. The group names must match exactly.

| Account type | Groups | Assignment | Status flags |
|---|---|---|---|
| NFE center data entry | `MSCC`, `MSCC_CENTER` (+ `EXPORT` to allow downloads) | Center and Partner | Active |
| NFE partner coordinator | `MSCC_PARTNER` | Partner | Active |
| Sector-wide NFE reader (UNICEF / ministry) | `MSCC_UNICEF` | none | Active |
| Sector-wide beneficiary list | `MSCC`, `MSCC_CENTER`, `MSCC_FULL` | Center and Partner | Active |
| ALP school focal point | `ALP_SCHOOL` | School | Active |
| CLM bridging staff | `CLM_Bridging` (+ `CLM_BRIDGING_ALL`, `CLM_TEACHER`, `CLM_ATTENDANCE` as needed) | as instructed by the CLM team | Active |
| System administrator | none required | none | Active, Staff status, Superuser status |
| Limited admin (for example user management only) | none required | none | Active, Staff status + model permissions (section 10) |

1. On the **Personal info** tab, type the school name in the **School** field and select it from the suggestions. The list only offers open schools.

    ![Figure 15](../screenshots/en/adm_32_school_autocomplete.png)

    *Figure 15 – Choosing the school of an ALP account*

2. The selected school is shown in the field. One account is linked to exactly one school.

    ![Figure 16](../screenshots/en/adm_30_alp_user_personal_info.png)

    *Figure 16 – ALP account with its school*

3. On the **Permissions** tab the only group needed is `ALP_SCHOOL`.

    ![Figure 17](../screenshots/en/adm_31_alp_user_permissions.png)

    *Figure 17 – Groups of an ALP account*


## 7. Modifying an Account

1. Open the user from the list (click the username). Change the values on the **Account**, **Personal info** or **Permissions** tabs and click **Save**, or **Save and continue editing** to stay on the page.

    ![Figure 18](../screenshots/en/adm_22_add_user_saved.png)

    *Figure 18 – The user form*

2. When a staff member moves to another center or school, update the **assignment** and the **groups** together, then ask the user to log out and in again.
3. **History** (right-hand buttons) lists every change made to the account from the admin panel, with the date and the administrator who made it.

    ![Figure 19](../screenshots/en/adm_62_user_history.png)

    *Figure 19 – Change history of an account*


> **Note:** Do not reuse an old account for a new person: create a new account and deactivate the old one, so that the records created by each person stay traceable.

## 8. Resetting a Password

There is no self-service password reset in the application: users who forget their password contact the administrator.

1. Open the user and click **Reset password** in the **Account** tab (under the password hash).

    ![Figure 20](../screenshots/en/adm_40_reset_password_empty.png)

    *Figure 20 – The reset password form*

2. Enter the new password twice. It must follow the password rules of section 5.

    ![Figure 21](../screenshots/en/adm_41_reset_password_filled.png)

    *Figure 21 – New password entered*

3. Click **Change password**. A confirmation appears; communicate the password securely and ask the user to change it after login.

    ![Figure 22](../screenshots/en/adm_42_reset_password_done.png)

    *Figure 22 – Password changed*


> **Note:** After five failed login attempts in five minutes an account is temporarily blocked. The block lifts by itself after a few minutes; resetting the password is not required.

## 9. Deactivating, Reactivating and Deleting Accounts

**Deactivate** accounts of people who leave; do not delete them. A deactivated account cannot log in, but the registrations, attendance and exports it created keep their author.

1. In the users list tick the accounts, choose **Disable** in the action list and click **Go**. To re-enable, use **Activate**. You can also untick **Active** on the Permissions tab of one user.

    ![Figure 23](../screenshots/en/adm_50_action_disable.png)

    *Figure 23 – Bulk action "Disable"*

2. The **Active** column shows a red icon for disabled accounts. Use the **active** filter to list them.

    ![Figure 24](../screenshots/en/adm_51_user_disabled.png)

    *Figure 24 – A disabled account*

3. **Delete** (red button on the user form, or the **Delete selected users** action) first shows a confirmation page listing everything that will be removed with the account. Deleting cannot be undone; reserve it for accounts created by mistake that never entered data.

    ![Figure 25](../screenshots/en/adm_52_delete_user_confirm.png)

    *Figure 25 – Delete confirmation page*


## 10. Groups and Permissions

Groups are managed under **Authentication and Authorization → Groups** (reachable from the dashboard search or the address `/admin/auth/group/`).

1. The list shows the groups that exist. The application recognises the names of section 2; a group with another name has no effect in the application.

    ![Figure 26](../screenshots/en/adm_60_groups_list.png)

    *Figure 26 – The groups list*

2. Opening a group shows its **model permissions** (add / change / delete / view for each table). These permissions only matter for staff accounts that use the admin panel without superuser status. The roles of section 2 work without any model permission.

    ![Figure 27](../screenshots/en/adm_61_group_change.png)

    *Figure 27 – A group and its model permissions*


- Tick **Staff status** (not Superuser status) on the user.
- Create a group such as `ADMIN_USERS` with the permissions **Can view user**, **Can change user**, **Can add user** and add the user to it, or move the same permissions into the **User permissions** box of the user.
- The person then sees only the Users table in the admin panel. Do the same with the Center, School or Round permissions for reference-data administrators.

> **Note:** Never give **Superuser status** to an account used for daily data entry, and keep the number of superusers small.

## 11. Reference Data

The lists below drive the drop-downs of the application. Add or correct entries here; do not delete entries that are already used by registrations.

1. **Schools → Partner organizations**: the implementing partners. A partner must exist before centers and accounts can be linked to it.

    ![Figure 28](../screenshots/en/adm_70_partners.png)

    *Figure 28 – Partner organisations*

2. The partner form holds the short name and the focal points (monitoring and evaluation, programme manager).

    ![Figure 29](../screenshots/en/adm_71_partner_change.png)

    *Figure 29 – Partner organisation form*

3. **Locations → Centers**: the NFE centers with their partner, type, governorate, district and cadaster.

    ![Figure 30](../screenshots/en/adm_72_centers.png)

    *Figure 30 – Centers*

4. The center form also records the manager, phone, GPS coordinates (used by the Centers Map), accessibility and the packages provided.

    ![Figure 31](../screenshots/en/adm_73_center_change.png)

    *Figure 31 – Center form*

5. **Schools → Schools**: the public schools of the ALP module. Each ALP account is linked to one of them; closed schools are not offered when assigning accounts.

    ![Figure 32](../screenshots/en/adm_74_schools.png)

    *Figure 32 – Schools*

6. The school form: CERD number, name, type, shift, contact, location and services. School focal points maintain most of it themselves from the application.

    ![Figure 33](../screenshots/en/adm_75_school_change.png)

    *Figure 33 – School form*

7. **NFE Data → Rounds**: the programme rounds (years). Tick **Current year** on the round(s) open for registration: only current rounds are offered in the enrolment and attendance forms.

    ![Figure 34](../screenshots/en/adm_76_rounds.png)

    *Figure 34 – Rounds*

8. A round has a name, a year and the current-year flag. Create the new round before the new year starts and untick the previous one when it closes.

    ![Figure 35](../screenshots/en/adm_77_round_change.png)

    *Figure 35 – Round form*

9. **ALP → ALP Rounds** and **ALP Programs**: the academic years and programme levels offered in ALP registration.

    ![Figure 36](../screenshots/en/adm_78_alp_rounds.png)

    *Figure 36 – ALP rounds*

10. **ALP → ALP Grading Definitions**: one line per subject with its minimum and maximum grade. The ALP grading form is built from this list.

    ![Figure 37](../screenshots/en/adm_80_alp_grading_definitions.png)

    *Figure 37 – ALP grading definitions*

11. **NFE Data → Packages**: the education programmes with the age range they accept. A child only sees the programmes whose age range includes their age; the attendance page lists the packages of category "Education".

    ![Figure 38](../screenshots/en/adm_81_packages.png)

    *Figure 38 – Packages*

12. **Child data config → Nationalities, ID Types, Attachment Types, Topics of teacher trainings** and **Schools → Educational levels**: the lookup values of the registration and teacher forms.

    ![Figure 39](../screenshots/en/adm_82_nationalities.png)

    *Figure 39 – Nationalities*

13. **Locations → Locations**: the governorate / district / cadaster hierarchy (Location Types 1, 2 and 3). Keep the Arabic and English names filled in; they are matched against the examination village list.

    ![Figure 40](../screenshots/en/adm_83_locations.png)

    *Figure 40 – Locations*


## 12. Monitoring

1. **Backends → User activitys** logs who did what and when in the application. Filter by user or date when investigating a question.

    ![Figure 41](../screenshots/en/adm_90_user_activity.png)

    *Figure 41 – User activity log*

2. **Backends → Export History** lists every export requested, its status and file. Failed exports are visible here.

    ![Figure 42](../screenshots/en/adm_91_export_history.png)

    *Figure 42 – Export history*

3. **Celery Config → Task run logs** shows the background tasks (exports, scheduled jobs) and their result.

    ![Figure 43](../screenshots/en/adm_92_task_logs.png)

    *Figure 43 – Task run logs*

4. **NFE Data → Registrations** and **Child → Childs** give direct access to the records. Use them for corrections that the application does not allow (for example cancelling a registration), and only after checking with the center.

    ![Figure 44](../screenshots/en/adm_93_registrations.png)

    *Figure 44 – Registrations in the admin panel*


## 13. Good Practices

- **One person, one account.** Never share credentials between staff; create a separate account for each person.
- **Least privilege.** Give only the groups and the assignment the person needs. Avoid `MSCC_FULL` and superuser status unless required.
- **Review accounts regularly.** Export the user list every quarter, deactivate leavers and check assignments.
- **Deactivate, do not delete**, so that the audit trail is preserved.
- **Secure credentials.** Send initial passwords through a secure channel and ask for a change at first login.
- **Log out** of the admin panel when leaving the computer; the session also expires automatically after inactivity.

## 14. Frequently Asked Questions

| Question | Answer |
|---|---|
| A user logs in but every list is empty. | The assignment is missing: set the center (and partner) or the school on the Personal info tab, matching the groups. |
| A user gets "403 / permission denied" on a page. | The account lacks the group that unlocks that page. Compare with the role recipes of section 6. |
| The user cannot open the admin panel. | Tick Staff status, and give model permissions or superuser status (section 10). |
| A superuser cannot add an ALP registration. | This is intended: ALP data is entered by the school accounts only. |
| Which round is offered in the forms? | Only rounds with the Current year flag (NFE) or the current ALP round. |
| A programme is missing from the child registration. | Check the age range of the package and the child's date of birth. |
| Can I rename a group? | No. The application checks the exact names; renaming a group removes the access of all its members. |
| How do I know who changed a record? | Open the record and click History, or consult the User activity log. |
