# -*- coding: utf-8 -*-
# flake8: noqa
"""Content of the Admin Panel manual (English and Arabic): user management and permissions."""

GROUPS_EN = [
    ['`MSCC`', 'NFE data entry: registrations, services, assessments, attendance of the assigned center'],
    ['`MSCC_CENTER`', 'Limits the NFE lists to the center linked to the account. Combine with `MSCC`'],
    ['`MSCC_PARTNER`', 'Read-oriented view over all the centers of the partner organisation linked to the account'],
    ['`MSCC_FULL`', 'Removes the center/partner filter on the NFE beneficiary list (sector-wide view)'],
    ['`MSCC_UNICEF`', 'Sector-wide analytics, reports and exports for UNICEF staff'],
    ['`EXPORT`', 'Unlocks the export buttons on lists that gate them'],
    ['`YOUTH`', 'Marks youth-stream accounts (used by the admin "User Category" filter)'],
    ['`ALP_SCHOOL`', 'ALP school focal point. Required for every ALP page; data limited to the linked school'],
    ['`CLM_Bridging`, `CLM_BRIDGING_ALL`, `CLM_ATTENDANCE`, `CLM_TEACHER`, `CLM_Inclusion`', 'Community Learning (bridging) module roles'],
]
GROUPS_AR = [
    ['`MSCC`', 'إدخال بيانات التعليم غير النظامي: التسجيلات والخدمات والتقييمات والحضور للمركز المرتبط'],
    ['`MSCC_CENTER`', 'يحصر قوائم التعليم غير النظامي بالمركز المرتبط بالحساب. يُستخدم مع `MSCC`'],
    ['`MSCC_PARTNER`', 'اطّلاع على جميع مراكز المنظمة الشريكة المرتبطة بالحساب'],
    ['`MSCC_FULL`', 'يزيل فلتر المركز/الشريك من قائمة المستفيدين (عرض على مستوى القطاع)'],
    ['`MSCC_UNICEF`', 'تحليلات وتقارير وتصدير على مستوى القطاع لموظفي اليونيسف'],
    ['`EXPORT`', 'يفعّل أزرار التصدير في القوائم التي تقيّدها'],
    ['`YOUTH`', 'يميّز حسابات مسار الشباب (يستخدمه فلتر "فئة المستخدم" في لوحة الإدارة)'],
    ['`ALP_SCHOOL`', 'نقطة اتصال مدرسة التعليم المسرّع. مطلوبة لكل صفحات ALP؛ البيانات محصورة بالمدرسة المرتبطة'],
    ['`CLM_Bridging`, `CLM_BRIDGING_ALL`, `CLM_ATTENDANCE`, `CLM_TEACHER`, `CLM_Inclusion`', 'أدوار وحدة التعلّم المجتمعي (الجسر)'],
]

EN = {
    'title': 'Admin Panel – User Management and Permissions',
    'subtitle': 'BMA Platform – Administrator Manual',
    'audience': 'For system administrators and staff who manage accounts, roles and reference data',
    'intro': [
        'This manual explains how to use the **administration panel** of the BMA platform. It focuses on **user management '
        'and permissions**: creating accounts, assigning roles and the center, partner or school each account may see, resetting '
        'passwords, deactivating accounts and understanding what every role can do. It also covers the reference tables the '
        'administrator maintains (partners, centers, schools, rounds, programmes) and the monitoring pages.',
        'The administration panel is reserved for accounts with **staff status**. A **superuser** has every right; a staff '
        'account without superuser status only sees the pages it was explicitly granted (see section 10). Changes made here apply '
        '**immediately** to the field users, so always double-check before saving.',
        'Each step is illustrated with a screenshot taken from the system. The data shown is demonstration data only.',
    ],
    'sections': [
        # 1 -----------------------------------------------------------------
        {'title': 'Accessing the Admin Panel', 'body': [
            ('p', 'Open the platform address followed by **/admin/** (for example `https://<platform>/admin/`). You can also open it '
                  'from the user menu of the application, entry **Admin**, when your account has staff status.'),
            ('steps', [
                ('Enter your **username** and **password** on the administration login page.', 'adm_00_login_empty.png', 'Administration login page'),
                ('Click **Log in**. Only accounts with staff status are accepted; other accounts receive an error.', 'adm_00_login_filled.png', 'Login form filled in'),
                ('The **Dashboard** lists every data table you may manage, grouped by area: NFE data, Attendances, Child data '
                 'configuration, Schools, Locations, Users, Backends (monitoring), ALP and configuration. **Recent actions** on the right '
                 'shows the last changes made by your account.', 'adm_01_dashboard.png', 'The administration dashboard'),
                ('The **left menu** lists the same tables; the **top bar** gives quick access to Users, Schools and Locations. '
                 'The icon at the top right opens the user menu: **See site** (back to the application), **Change password** and **Log out**.',
                 'adm_02_user_menu.png', 'The user menu of the admin panel'),
            ]),
            ('note', 'The admin panel follows the language chosen in the application (globe icon). The interface and most labels are '
                     'translated; group names and technical identifiers are always shown as stored.'),
        ]},
        # 2 -----------------------------------------------------------------
        {'title': 'How Access Works', 'body': [
            ('p', 'What a user can see and do is decided by **three things** on the user record. All three must be consistent, '
                  'otherwise the user sees empty lists or a "permission denied" page.'),
            ('table', ['Setting', 'Where', 'Effect'], [
                ['**Status flags**', 'Permissions tab', '**Active** allows login. **Staff status** opens the admin panel. **Superuser status** grants every right everywhere.'],
                ['**Groups (roles)**', 'Permissions tab', 'Each group name unlocks a set of pages in the application: NFE, ALP or CLM pages, exports, sector-wide lists.'],
                ['**Assignment**', 'Personal info tab', 'The **center**, **partner** or **school** linked to the account. Lists, dashboards and exports are filtered to it.'],
            ]),
            ('h3', 'The roles (groups) in use'),
            ('p', 'The application checks the **group name** exactly as written. Create accounts with the existing groups below; do not '
                  'rename them and do not create new ones unless the development team has added the matching code.'),
            ('table', ['Group name', 'What it gives'], GROUPS_EN),
            ('h3', 'Rules to remember'),
            ('bullets', [
                'A **center user** needs `MSCC` + `MSCC_CENTER`, a **center** and the **partner** that runs it. Add `EXPORT` if the user may download data.',
                'A **partner coordinator** needs `MSCC_PARTNER` and the **partner**; no center.',
                'An **ALP school focal point** needs `ALP_SCHOOL` and a **school**. Without the school every ALP list stays empty.',
                'A **UNICEF or ministry reader** needs `MSCC_UNICEF` (or `MSCC_FULL` with `MSCC_CENTER` for the sector-wide list); no assignment is required.',
                'Superusers can **view** ALP data but can **never add or edit** it: ALP data entry is reserved for the school accounts.',
                'The **User permissions** box (individual model permissions) does not affect the application; it only matters for staff '
                'accounts that use the admin panel without superuser status (section 10).',
            ]),
        ]},
        # 3 -----------------------------------------------------------------
        {'title': 'Center, Partner or School – Choosing the Assignment', 'body': [
            ('p', 'The **Personal info** tab has three assignment fields: **Partner**, **Center** and **School**. Which ones you fill '
                  'depends on the kind of account, and the groups must match. This is the most frequent source of "empty lists" '
                  'and "permission denied" problems, so use the table below every time you create or modify an account.'),
            ('table', ['Account', 'Groups', 'Partner field', 'Center field', 'School field'], [
                ['Center data-entry user (works in one center)', '`MSCC` + `MSCC_CENTER`', '**Yes** – the partner that runs the center', '**Yes** – the one center', 'empty'],
                ['Partner coordinator (monitors all the centers of the organisation)', '`MSCC_PARTNER`', '**Yes** – the organisation', 'empty', 'empty'],
                ['UNICEF / ministry reader (whole sector)', '`MSCC_UNICEF`', 'empty', 'empty', 'empty'],
                ['ALP school focal point', '`ALP_SCHOOL`', 'empty', 'empty', '**Yes** – the one school'],
                ['Administrator', 'none (Staff + Superuser status)', 'empty', 'empty', 'empty'],
            ]),
            ('h3', 'MSCC_CENTER versus MSCC_PARTNER'),
            ('p', 'Both roles belong to the NFE module, but they serve different people and give different rights:'),
            ('table', ['', '`MSCC_CENTER` (with `MSCC`)', '`MSCC_PARTNER`'], [
                ['Who', 'A data-entry officer or facilitator working **in one center**', 'A coordinator or M&E officer of the **partner organisation**'],
                ['Scope of data', 'Only the children, attendance and teachers of the **center** linked to the account', 'The children, attendance and teachers of **all the centers** of the **partner** linked to the account'],
                ['Register children, record services, exams, attendance', '**Yes**', '**No** – read-only on registrations; can view and filter the lists'],
                ['Manage teachers', 'Yes, for the center', 'Yes, for all the centers of the partner'],
                ['Export beneficiary data', 'The center\'s registrations (with the `EXPORT` group where the list requires it)', 'All the partner\'s registrations'],
                ['Dashboards and heatmaps', 'The center', 'All the centers of the partner'],
                ['Required assignment', 'Center **and** Partner', 'Partner only'],
            ]),
            ('h3', 'When to select the Partner'),
            ('bullets', [
                'For every NFE account that belongs to an organisation: center users **and** partner coordinators.',
                'The partner is written on each registration the user creates, and it decides what a `MSCC_PARTNER` user can see.',
                'For a center user, choose the partner that **operates the center**. If the center is later moved to another partner, update the accounts of that center too.',
            ]),
            ('h3', 'When to select the Center'),
            ('bullets', [
                'Only for accounts that **enter data in one specific center** (`MSCC` + `MSCC_CENTER`).',
                'The attendance page, the registration form and the beneficiary list are filtered to this center; a center user with no center sees a warning and empty lists.',
                'Never give a center to a `MSCC_PARTNER` coordinator: it is ignored for their lists and only causes confusion. A person who works in two centers needs two accounts, or a partner-level account if read access is enough.',
            ]),
            ('h3', 'When to select the School'),
            ('bullets', [
                'Only for **ALP** accounts (`ALP_SCHOOL`). The school is the equivalent of the center for the ALP module: registrations, attendance, teachers, grades and dashboards are limited to it.',
                'Leave Partner and Center empty on an ALP account; they have no effect on ALP pages.',
                'The field only offers schools that are not closed. If the school is missing, create or reopen it under **Schools** first (section 11).',
            ]),
            ('note', 'Rule of thumb: **Center = enters data for one center**, **Partner = watches all the centers of an organisation**, '
                     '**School = ALP focal point**. One account should fit exactly one line of the first table.'),
        ]},
        # 3 -----------------------------------------------------------------
        {'title': 'The Users List', 'body': [
            ('p', 'Open **Users → Users** in the left menu (or the **Users** entry of the top bar).'),
            ('steps', [
                ('The list shows the username, names, active flag, email, school, center, partner, phone and the **user category** '
                 '(derived from the groups). Click a column header to sort. The **Add user** button creates an account; **Import** and '
                 '**Export** exchange the user list as a file.', 'adm_10_users_list.png', 'The users list'),
                ('Type a username, name or school in the search box and press **Search**.', 'adm_11_users_search.png', 'Searching users'),
                ('Use the filter lists above the table (**groups**, **school**, **center**, **Partner**, **active**, **User Category**) to '
                 'narrow the list, for example all the accounts of one center or every inactive account.', 'adm_12_users_filtered.png', 'Users filtered by group'),
                ('**Export** downloads the list (CSV, XLSX, JSON…) with the names, assignments, active flag and category of each user. '
                 'Use it for periodic access reviews.', 'adm_14_users_export.png', 'Exporting the user list'),
                ('**Import** loads a file in the same layout to create or update many accounts at once. Always use **Preview** first and '
                 'check the differences before confirming.', 'adm_15_users_import.png', 'Importing users'),
            ]),
            ('note', 'Passwords are never exported. Imported accounts have no usable password until you reset it (section 8).'),
        ]},
        # 4 -----------------------------------------------------------------
        {'title': 'Creating an Account', 'body': [
            ('p', 'Creating an account takes two screens: first the username and password, then the personal information, '
                  'assignment and roles.'),
            ('steps', [
                ('Click **Add user**. Enter the **username** (letters, digits and @ . + - _ only; it cannot be changed easily later) and the '
                 '**password** twice. Use the agreed naming convention, for example `firstname.lastname` or `center.city`.',
                 'adm_20_add_user_empty.png', 'The Add user form'),
                ('Click **Save**. The account is created and the full user form opens with the message "was added successfully".',
                 'adm_21_add_user_filled.png', 'Username and password filled in'),
                ('On the **Personal info** tab enter the first name, last name, email and phone, then the assignment: the **Partner** and '
                 '**Center** for an NFE account, or the **School** for an ALP account (type part of the school name and pick it from the list).',
                 'adm_23_add_user_personal_info.png', 'Personal info and assignment'),
                ('On the **Permissions** tab keep **Active** ticked. Tick **Staff status** only for administrators. In **Groups**, select the '
                 'roles in the left box and move them to the right box with the arrow (double-click also works). Leave **User permissions** empty.',
                 'adm_24_add_user_permissions.png', 'Groups chosen for a center data-entry account'),
                ('Click **Save**. The list reopens with a confirmation message. Give the credentials to the user through a secure channel and ask '
                 'them to change the password at first login.', 'adm_25_add_user_done.png', 'Account saved'),
            ]),
            ('table', ['Password rule', 'Requirement'], [
                ['Length', 'At least 8 characters'],
                ['Digits', 'At least 3 digits'],
                ['Letters', 'At least one upper-case and one lower-case letter'],
                ['Symbol', 'At least one symbol such as ! @ # $ % & *'],
                ['Not common', 'Not a common word and not similar to the username'],
            ]),
        ]},
        # 5 -----------------------------------------------------------------
        {'title': 'Role Recipes', 'body': [
            ('p', 'Use these combinations when creating accounts. The group names must match exactly.'),
            ('table', ['Account type', 'Groups', 'Assignment', 'Status flags'], [
                ['NFE center data entry', '`MSCC`, `MSCC_CENTER` (+ `EXPORT` to allow downloads)', 'Center and Partner', 'Active'],
                ['NFE partner coordinator', '`MSCC_PARTNER`', 'Partner', 'Active'],
                ['Sector-wide NFE reader (UNICEF / ministry)', '`MSCC_UNICEF`', 'none', 'Active'],
                ['Sector-wide beneficiary list', '`MSCC`, `MSCC_CENTER`, `MSCC_FULL`', 'Center and Partner', 'Active'],
                ['ALP school focal point', '`ALP_SCHOOL`', 'School', 'Active'],
                ['CLM bridging staff', '`CLM_Bridging` (+ `CLM_BRIDGING_ALL`, `CLM_TEACHER`, `CLM_ATTENDANCE` as needed)', 'as instructed by the CLM team', 'Active'],
                ['System administrator', 'none required', 'none', 'Active, Staff status, Superuser status'],
                ['Limited admin (for example user management only)', 'none required', 'none', 'Active, Staff status + model permissions (section 10)'],
            ]),
            ('h3', 'Example: an ALP school focal point'),
            ('steps', [
                ('On the **Personal info** tab, type the school name in the **School** field and select it from the suggestions. The list '
                 'only offers open schools.', 'adm_32_school_autocomplete.png', 'Choosing the school of an ALP account'),
                ('The selected school is shown in the field. One account is linked to exactly one school.', 'adm_30_alp_user_personal_info.png', 'ALP account with its school'),
                ('On the **Permissions** tab the only group needed is `ALP_SCHOOL`.', 'adm_31_alp_user_permissions.png', 'Groups of an ALP account'),
            ]),
        ]},
        # 6 -----------------------------------------------------------------
        {'title': 'Modifying an Account', 'body': [
            ('steps', [
                ('Open the user from the list (click the username). Change the values on the **Account**, **Personal info** or **Permissions** '
                 'tabs and click **Save**, or **Save and continue editing** to stay on the page.', 'adm_22_add_user_saved.png', 'The user form'),
                ('When a staff member moves to another center or school, update the **assignment** and the **groups** together, then ask the '
                 'user to log out and in again.', None, None),
                ('**History** (right-hand buttons) lists every change made to the account from the admin panel, with the date and the '
                 'administrator who made it.', 'adm_62_user_history.png', 'Change history of an account'),
            ]),
            ('note', 'Do not reuse an old account for a new person: create a new account and deactivate the old one, so that the records '
                     'created by each person stay traceable.'),
        ]},
        # 7 -----------------------------------------------------------------
        {'title': 'Resetting a Password', 'body': [
            ('p', 'There is no self-service password reset in the application: users who forget their password contact the administrator.'),
            ('steps', [
                ('Open the user and click **Reset password** in the **Account** tab (under the password hash).', 'adm_40_reset_password_empty.png', 'The reset password form'),
                ('Enter the new password twice. It must follow the password rules of section 5.', 'adm_41_reset_password_filled.png', 'New password entered'),
                ('Click **Change password**. A confirmation appears; communicate the password securely and ask the user to change it after login.',
                 'adm_42_reset_password_done.png', 'Password changed'),
            ]),
            ('note', 'After five failed login attempts in five minutes an account is temporarily blocked. The block lifts by itself after a few '
                     'minutes; resetting the password is not required.'),
        ]},
        # 8 -----------------------------------------------------------------
        {'title': 'Deactivating, Reactivating and Deleting Accounts', 'body': [
            ('p', '**Deactivate** accounts of people who leave; do not delete them. A deactivated account cannot log in, but the registrations, '
                  'attendance and exports it created keep their author.'),
            ('steps', [
                ('In the users list tick the accounts, choose **Disable** in the action list and click **Go**. To re-enable, use **Activate**. '
                 'You can also untick **Active** on the Permissions tab of one user.', 'adm_50_action_disable.png', 'Bulk action "Disable"'),
                ('The **Active** column shows a red icon for disabled accounts. Use the **active** filter to list them.', 'adm_51_user_disabled.png', 'A disabled account'),
                ('**Delete** (red button on the user form, or the **Delete selected users** action) first shows a confirmation page listing '
                 'everything that will be removed with the account. Deleting cannot be undone; reserve it for accounts created by mistake that never entered data.',
                 'adm_52_delete_user_confirm.png', 'Delete confirmation page'),
            ]),
        ]},
        # 9 -----------------------------------------------------------------
        {'title': 'Groups and Permissions', 'body': [
            ('p', 'Groups are managed under **Authentication and Authorization → Groups** (reachable from the dashboard search or the '
                  'address `/admin/auth/group/`).'),
            ('steps', [
                ('The list shows the groups that exist. The application recognises the names of section 2; a group with another name has no '
                 'effect in the application.', 'adm_60_groups_list.png', 'The groups list'),
                ('Opening a group shows its **model permissions** (add / change / delete / view for each table). These permissions only matter for '
                 'staff accounts that use the admin panel without superuser status. The roles of section 2 work without any model permission.',
                 'adm_61_group_change.png', 'A group and its model permissions'),
            ]),
            ('h3', 'Giving someone limited admin access'),
            ('bullets', [
                'Tick **Staff status** (not Superuser status) on the user.',
                'Create a group such as `ADMIN_USERS` with the permissions **Can view user**, **Can change user**, **Can add user** and add the user to it, '
                'or move the same permissions into the **User permissions** box of the user.',
                'The person then sees only the Users table in the admin panel. Do the same with the Center, School or Round permissions for '
                'reference-data administrators.',
            ]),
            ('note', 'Never give **Superuser status** to an account used for daily data entry, and keep the number of superusers small.'),
        ]},
        # 10 ----------------------------------------------------------------
        {'title': 'Reference Data', 'body': [
            ('p', 'The lists below drive the drop-downs of the application. Add or correct entries here; do not delete entries that are '
                  'already used by registrations.'),
            ('steps', [
                ('**Schools → Partner organizations**: the implementing partners. A partner must exist before centers and accounts can be linked to it.',
                 'adm_70_partners.png', 'Partner organisations'),
                ('The partner form holds the short name and the focal points (monitoring and evaluation, programme manager).',
                 'adm_71_partner_change.png', 'Partner organisation form'),
                ('**Locations → Centers**: the NFE centers with their partner, type, governorate, district and cadaster.', 'adm_72_centers.png', 'Centers'),
                ('The center form also records the manager, phone, GPS coordinates (used by the Centers Map), accessibility and the packages provided.',
                 'adm_73_center_change.png', 'Center form'),
                ('**Schools → Schools**: the public schools of the ALP module. Each ALP account is linked to one of them; closed schools are not offered when assigning accounts.',
                 'adm_74_schools.png', 'Schools'),
                ('The school form: CERD number, name, type, shift, contact, location and services. School focal points maintain most of it themselves from the application.',
                 'adm_75_school_change.png', 'School form'),
                ('**NFE Data → Rounds**: the programme rounds (years). Tick **Current year** on the round(s) open for registration: only current rounds are offered in the '
                 'enrolment and attendance forms.', 'adm_76_rounds.png', 'Rounds'),
                ('A round has a name, a year and the current-year flag. Create the new round before the new year starts and untick the previous one when it closes.',
                 'adm_77_round_change.png', 'Round form'),
                ('**ALP → ALP Rounds** and **ALP Programs**: the academic years and programme levels offered in ALP registration.', 'adm_78_alp_rounds.png', 'ALP rounds'),
                ('**ALP → ALP Grading Definitions**: one line per subject with its minimum and maximum grade. The ALP grading form is built from this list.',
                 'adm_80_alp_grading_definitions.png', 'ALP grading definitions'),
                ('**NFE Data → Packages**: the education programmes with the age range they accept. A child only sees the programmes whose age range '
                 'includes their age; the attendance page lists the packages of category "Education".', 'adm_81_packages.png', 'Packages'),
                ('**Child data config → Nationalities, ID Types, Attachment Types, Topics of teacher trainings** and **Schools → Educational levels**: '
                 'the lookup values of the registration and teacher forms.', 'adm_82_nationalities.png', 'Nationalities'),
                ('**Locations → Locations**: the governorate / district / cadaster hierarchy (Location Types 1, 2 and 3). Keep the Arabic and English names '
                 'filled in; they are matched against the examination village list.', 'adm_83_locations.png', 'Locations'),
            ]),
        ]},
        # 11 ----------------------------------------------------------------
        {'title': 'Monitoring', 'body': [
            ('steps', [
                ('**Backends → User activitys** logs who did what and when in the application. Filter by user or date when investigating a question.',
                 'adm_90_user_activity.png', 'User activity log'),
                ('**Backends → Export History** lists every export requested, its status and file. Failed exports are visible here.',
                 'adm_91_export_history.png', 'Export history'),
                ('**Celery Config → Task run logs** shows the background tasks (exports, scheduled jobs) and their result.', 'adm_92_task_logs.png', 'Task run logs'),
                ('**NFE Data → Registrations** and **Child → Childs** give direct access to the records. Use them for corrections that the '
                 'application does not allow (for example cancelling a registration), and only after checking with the center.',
                 'adm_93_registrations.png', 'Registrations in the admin panel'),
            ]),
        ]},
        # 12 ----------------------------------------------------------------
        {'title': 'Good Practices', 'body': [
            ('bullets', [
                '**One person, one account.** Never share credentials between staff; create a separate account for each person.',
                '**Least privilege.** Give only the groups and the assignment the person needs. Avoid `MSCC_FULL` and superuser status unless required.',
                '**Review accounts regularly.** Export the user list every quarter, deactivate leavers and check assignments.',
                '**Deactivate, do not delete**, so that the audit trail is preserved.',
                '**Secure credentials.** Send initial passwords through a secure channel and ask for a change at first login.',
                '**Log out** of the admin panel when leaving the computer; the session also expires automatically after inactivity.',
            ]),
        ]},
        # 13 ----------------------------------------------------------------
        {'title': 'Frequently Asked Questions', 'body': [
            ('table', ['Question', 'Answer'], [
                ['A user logs in but every list is empty.', 'The assignment is missing: set the center (and partner) or the school on the Personal info tab, matching the groups.'],
                ['A user gets "403 / permission denied" on a page.', 'The account lacks the group that unlocks that page. Compare with the role recipes of section 6.'],
                ['The user cannot open the admin panel.', 'Tick Staff status, and give model permissions or superuser status (section 10).'],
                ['A superuser cannot add an ALP registration.', 'This is intended: ALP data is entered by the school accounts only.'],
                ['Which round is offered in the forms?', 'Only rounds with the Current year flag (NFE) or the current ALP round.'],
                ['A programme is missing from the child registration.', 'Check the age range of the package and the child\'s date of birth.'],
                ['Can I rename a group?', 'No. The application checks the exact names; renaming a group removes the access of all its members.'],
                ['How do I know who changed a record?', 'Open the record and click History, or consult the User activity log.'],
            ]),
        ]},
    ],
}

AR = {
    'title': 'لوحة الإدارة – إدارة المستخدمين والصلاحيات',
    'subtitle': 'منصة BMA – دليل المدير',
    'audience': 'لمديري النظام والموظفين الذين يديرون الحسابات والأدوار والبيانات المرجعية',
    'intro': [
        'يشرح هذا الدليل كيفية استخدام **لوحة الإدارة** في منصة BMA. ويركّز على **إدارة المستخدمين والصلاحيات**: إنشاء الحسابات، '
        'وتعيين الأدوار والمركز أو الشريك أو المدرسة التي يمكن لكل حساب رؤيتها، وإعادة تعيين كلمات المرور، وتعطيل الحسابات، وفهم ما يستطيع '
        'كل دور القيام به. كما يغطّي الجداول المرجعية التي يصونها المدير (الشركاء، المراكز، المدارس، الدورات، البرامج) وصفحات المراقبة.',
        'لوحة الإدارة مخصّصة للحسابات التي تحمل **صفة موظف (Staff)**. **المستخدم الخارق (Superuser)** يملك كل الصلاحيات؛ أمّا حساب الموظف '
        'من دون صفة المستخدم الخارق فلا يرى إلا الصفحات الممنوحة له صراحةً (انظر القسم 10). التغييرات هنا تُطبَّق **فوراً** على المستخدمين الميدانيين، '
        'لذا تحقّق دائماً قبل الحفظ.',
        'كل خطوة مرفقة بلقطة شاشة مأخوذة من النظام. البيانات الظاهرة هي بيانات تجريبية فقط.',
    ],
    'sections': [
        # 1 -----------------------------------------------------------------
        {'title': 'الدخول إلى لوحة الإدارة', 'body': [
            ('p', 'افتح عنوان المنصة متبوعاً بـ **/admin/** (مثلاً `https://<platform>/admin/`). يمكنك أيضاً فتحها من قائمة المستخدم في التطبيق '
                  'عبر عنصر **الإدارة** إذا كان حسابك يحمل صفة موظف.'),
            ('steps', [
                ('أدخل **اسم المستخدم** و**كلمة المرور** في صفحة دخول لوحة الإدارة.', 'adm_00_login_empty.png', 'صفحة دخول لوحة الإدارة'),
                ('اضغط **تسجيل الدخول**. تُقبل حسابات الموظفين فقط؛ تتلقّى الحسابات الأخرى رسالة خطأ.', 'adm_00_login_filled.png', 'نموذج الدخول بعد تعبئته'),
                ('تعرض **لوحة التحكّم** كل جداول البيانات التي يمكنك إدارتها مجمّعة بحسب المجال: بيانات التعليم غير النظامي، الحضور، إعدادات بيانات الطفل، '
                 'المدارس، المواقع، المستخدمون، المراقبة، ALP والإعدادات. يعرض قسم **الإجراءات الأخيرة** على الجانب آخر التغييرات التي أجراها حسابك.',
                 'adm_01_dashboard.png', 'لوحة تحكّم الإدارة'),
                ('تعرض **القائمة الجانبية** الجداول نفسها؛ ويتيح **الشريط العلوي** وصولاً سريعاً إلى المستخدمين والمدارس والمواقع. تفتح الأيقونة في أعلى الصفحة قائمة المستخدم: '
                 '**عرض الموقع** (العودة إلى التطبيق)، **تغيير كلمة المرور** و**تسجيل الخروج**.', 'adm_02_user_menu.png', 'قائمة المستخدم في لوحة الإدارة'),
            ]),
            ('note', 'تتبع لوحة الإدارة اللغة المختارة في التطبيق (أيقونة الكرة الأرضية). الواجهة ومعظم التسميات مترجمة؛ أمّا أسماء المجموعات والمعرّفات التقنية فتظهر دائماً كما هي مخزّنة.'),
        ]},
        # 2 -----------------------------------------------------------------
        {'title': 'كيف تعمل الصلاحيات', 'body': [
            ('p', 'يحدَّد ما يراه المستخدم وما يستطيع فعله بـ **ثلاثة عناصر** في سجل المستخدم. يجب أن تكون العناصر الثلاثة متّسقة، وإلا رأى المستخدم قوائم فارغة أو صفحة "غير مسموح".'),
            ('table', ['الإعداد', 'مكانه', 'الأثر'], [
                ['**علامات الحالة**', 'تبويبة الصلاحيات', '**نشط** يسمح بتسجيل الدخول. **صفة موظف** تفتح لوحة الإدارة. **مستخدم خارق** يمنح كل الصلاحيات في كل مكان.'],
                ['**المجموعات (الأدوار)**', 'تبويبة الصلاحيات', 'كل اسم مجموعة يفتح مجموعة من صفحات التطبيق: صفحات NFE أو ALP أو CLM، التصدير، القوائم على مستوى القطاع.'],
                ['**الارتباط**', 'تبويبة المعلومات الشخصية', '**المركز** أو **الشريك** أو **المدرسة** المرتبطة بالحساب. تُصفّى القوائم ولوحات المعلومات والتصدير بحسبها.'],
            ]),
            ('h3', 'الأدوار (المجموعات) المستخدمة'),
            ('p', 'يتحقّق التطبيق من **اسم المجموعة** كما هو مكتوب بالضبط. أنشئ الحسابات بالمجموعات الموجودة أدناه؛ لا تُعد تسميتها ولا تُنشئ مجموعات جديدة ما لم يضف فريق التطوير الكود المقابل.'),
            ('table', ['اسم المجموعة', 'ما تمنحه'], GROUPS_AR),
            ('h3', 'قواعد يجب تذكّرها'),
            ('bullets', [
                '**مستخدم المركز** يحتاج `MSCC` + `MSCC_CENTER` و**مركزاً** و**الشريك** الذي يديره. أضف `EXPORT` إذا كان يجوز له تحميل البيانات.',
                '**منسّق الشريك** يحتاج `MSCC_PARTNER` و**الشريك**؛ من دون مركز.',
                '**نقطة اتصال مدرسة ALP** تحتاج `ALP_SCHOOL` و**مدرسة**. من دون المدرسة تبقى كل قوائم ALP فارغة.',
                '**قارئ اليونيسف أو الوزارة** يحتاج `MSCC_UNICEF` (أو `MSCC_FULL` مع `MSCC_CENTER` للقائمة على مستوى القطاع)؛ لا يلزم ارتباط.',
                'يستطيع المستخدمون الخارقون **عرض** بيانات ALP لكن لا يمكنهم **أبداً إضافتها أو تعديلها**: إدخال بيانات ALP محصور بحسابات المدارس.',
                'مربّع **صلاحيات المستخدم** (صلاحيات النماذج الفردية) لا يؤثّر على التطبيق؛ يهمّ فقط حسابات الموظفين التي تستخدم لوحة الإدارة من دون صفة المستخدم الخارق (القسم 10).',
            ]),
        ]},
        # 3 -----------------------------------------------------------------
        {'title': 'المركز أم الشريك أم المدرسة – اختيار الارتباط', 'body': [
            ('p', 'تحتوي تبويبة **المعلومات الشخصية** على ثلاثة حقول ارتباط: **الشريك** و**المركز** و**المدرسة**. يعتمد ما تملؤه على نوع الحساب، '
                  'ويجب أن تتطابق المجموعات معه. هذا هو المصدر الأكثر شيوعاً لمشاكل "القوائم الفارغة" و"غير مسموح"، لذا استخدم الجدول أدناه في كل مرة تنشئ أو تعدّل حساباً.'),
            ('table', ['الحساب', 'المجموعات', 'حقل الشريك', 'حقل المركز', 'حقل المدرسة'], [
                ['مستخدم إدخال بيانات في مركز (يعمل في مركز واحد)', '`MSCC` + `MSCC_CENTER`', '**نعم** – الشريك الذي يدير المركز', '**نعم** – المركز الواحد', 'فارغ'],
                ['منسّق الشريك (يتابع جميع مراكز المنظمة)', '`MSCC_PARTNER`', '**نعم** – المنظمة', 'فارغ', 'فارغ'],
                ['قارئ اليونيسف / الوزارة (القطاع كله)', '`MSCC_UNICEF`', 'فارغ', 'فارغ', 'فارغ'],
                ['نقطة اتصال مدرسة ALP', '`ALP_SCHOOL`', 'فارغ', 'فارغ', '**نعم** – المدرسة الواحدة'],
                ['المدير', 'لا شيء (صفة موظف + مستخدم خارق)', 'فارغ', 'فارغ', 'فارغ'],
            ]),
            ('h3', 'الفرق بين MSCC_CENTER و MSCC_PARTNER'),
            ('p', 'ينتمي الدوران إلى وحدة التعليم غير النظامي، لكنهما يخدمان أشخاصاً مختلفين ويمنحان صلاحيات مختلفة:'),
            ('table', ['', '`MSCC_CENTER` (مع `MSCC`)', '`MSCC_PARTNER`'], [
                ['من', 'موظف إدخال بيانات أو ميسّر يعمل **في مركز واحد**', 'منسّق أو مسؤول متابعة وتقييم في **المنظمة الشريكة**'],
                ['نطاق البيانات', 'أطفال وحضور ومعلّمو **المركز** المرتبط بالحساب فقط', 'أطفال وحضور ومعلّمو **جميع مراكز** **الشريك** المرتبط بالحساب'],
                ['تسجيل الأطفال وتوثيق الخدمات والامتحانات والحضور', '**نعم**', '**لا** – اطّلاع فقط على التسجيلات؛ يمكنه عرض القوائم وتصفيتها'],
                ['إدارة المعلّمين', 'نعم، للمركز', 'نعم، لجميع مراكز الشريك'],
                ['تصدير بيانات المستفيدين', 'تسجيلات المركز (مع مجموعة `EXPORT` حيث تتطلّبها القائمة)', 'جميع تسجيلات الشريك'],
                ['لوحات المعلومات والخرائط الحرارية', 'المركز', 'جميع مراكز الشريك'],
                ['الارتباط المطلوب', 'المركز **و**الشريك', 'الشريك فقط'],
            ]),
            ('h3', 'متى تختار الشريك'),
            ('bullets', [
                'لكل حساب في التعليم غير النظامي تابع لمنظمة: مستخدمو المراكز **و**منسّقو الشركاء.',
                'يُكتب الشريك على كل تسجيل ينشئه المستخدم، وهو الذي يحدّد ما يراه مستخدم `MSCC_PARTNER`.',
                'لمستخدم المركز اختر الشريك الذي **يشغّل المركز**. إذا نُقل المركز لاحقاً إلى شريك آخر، حدّث حسابات ذلك المركز أيضاً.',
            ]),
            ('h3', 'متى تختار المركز'),
            ('bullets', [
                'فقط للحسابات التي **تُدخل بيانات في مركز محدّد** (`MSCC` + `MSCC_CENTER`).',
                'تُصفّى صفحة الحضور ونموذج التسجيل وقائمة المستفيدين بحسب هذا المركز؛ مستخدم المركز من دون مركز يرى تنبيهاً وقوائم فارغة.',
                'لا تعطِ مركزاً أبداً لمنسّق `MSCC_PARTNER`: يُتجاهل في قوائمه ويسبّب الالتباس فقط. الشخص الذي يعمل في مركزين يحتاج حسابين، أو حساباً على مستوى الشريك إذا كان الاطّلاع كافياً.',
            ]),
            ('h3', 'متى تختار المدرسة'),
            ('bullets', [
                'فقط لحسابات **ALP** (`ALP_SCHOOL`). المدرسة هي ما يعادل المركز في وحدة ALP: التسجيلات والحضور والمعلّمون والدرجات ولوحات المعلومات محصورة بها.',
                'اترك الشريك والمركز فارغين في حساب ALP؛ لا أثر لهما على صفحات ALP.',
                'لا يعرض الحقل إلا المدارس غير المغلقة. إذا كانت المدرسة غير موجودة، أنشئها أو أعد فتحها تحت **المدارس** أولاً (القسم 11).',
            ]),
            ('note', 'قاعدة بسيطة: **المركز = يُدخل بيانات مركز واحد**، **الشريك = يتابع جميع مراكز منظمة**، **المدرسة = نقطة اتصال ALP**. '
                     'يجب أن ينطبق على كل حساب سطر واحد بالضبط من الجدول الأول.'),
        ]},
        # 3 -----------------------------------------------------------------
        {'title': 'قائمة المستخدمين', 'body': [
            ('p', 'افتح **المستخدمون ← المستخدمون** من القائمة الجانبية (أو عنصر **المستخدمون** في الشريط العلوي).'),
            ('steps', [
                ('تعرض القائمة اسم المستخدم والأسماء وعلامة النشاط والبريد الإلكتروني والمدرسة والمركز والشريك والهاتف و**فئة المستخدم** (المشتقّة من المجموعات). '
                 'اضغط عنوان العمود للفرز. زر **إضافة مستخدم** ينشئ حساباً؛ **استيراد** و**تصدير** يتبادلان قائمة المستخدمين كملف.', 'adm_10_users_list.png', 'قائمة المستخدمين'),
                ('اكتب اسم مستخدم أو اسماً أو مدرسة في مربّع البحث واضغط **بحث**.', 'adm_11_users_search.png', 'البحث عن مستخدمين'),
                ('استخدم قوائم التصفية فوق الجدول (**المجموعات**، **المدرسة**، **المركز**، **الشريك**، **نشط**، **فئة المستخدم**) لتضييق القائمة، مثلاً كل حسابات مركز واحد أو كل الحسابات غير النشطة.',
                 'adm_12_users_filtered.png', 'المستخدمون مصفّون بحسب المجموعة'),
                ('**تصدير** يحمّل القائمة (CSV، XLSX، JSON...) مع الأسماء والارتباطات وعلامة النشاط وفئة كل مستخدم. استخدمه للمراجعات الدورية للصلاحيات.',
                 'adm_14_users_export.png', 'تصدير قائمة المستخدمين'),
                ('**استيراد** يحمّل ملفاً بالتخطيط نفسه لإنشاء أو تحديث حسابات كثيرة دفعة واحدة. استخدم **المعاينة** أولاً وتحقّق من الفروقات قبل التأكيد.',
                 'adm_15_users_import.png', 'استيراد المستخدمين'),
            ]),
            ('note', 'لا تُصدَّر كلمات المرور أبداً. الحسابات المستوردة ليس لها كلمة مرور صالحة حتى تعيد تعيينها (القسم 8).'),
        ]},
        # 4 -----------------------------------------------------------------
        {'title': 'إنشاء حساب', 'body': [
            ('p', 'يتم إنشاء الحساب عبر شاشتين: أولاً اسم المستخدم وكلمة المرور، ثم المعلومات الشخصية والارتباط والأدوار.'),
            ('steps', [
                ('اضغط **إضافة مستخدم**. أدخل **اسم المستخدم** (أحرف وأرقام و @ . + - _ فقط؛ يصعب تغييره لاحقاً) و**كلمة المرور** مرتين. اتّبع اصطلاح التسمية المتّفق عليه، مثلاً `firstname.lastname` أو `center.city`.',
                 'adm_20_add_user_empty.png', 'نموذج إضافة مستخدم'),
                ('اضغط **حفظ**. يُنشأ الحساب ويُفتح نموذج المستخدم الكامل مع رسالة "تمت الإضافة بنجاح".', 'adm_21_add_user_filled.png', 'اسم المستخدم وكلمة المرور بعد التعبئة'),
                ('في تبويبة **المعلومات الشخصية** أدخل الاسم الأول والأخير والبريد الإلكتروني والهاتف، ثم الارتباط: **الشريك** و**المركز** لحساب التعليم غير النظامي، '
                 'أو **المدرسة** لحساب ALP (اكتب جزءاً من اسم المدرسة واخترها من القائمة).', 'adm_23_add_user_personal_info.png', 'المعلومات الشخصية والارتباط'),
                ('في تبويبة **الصلاحيات** أبقِ **نشط** معلَّماً. علّم **صفة موظف** للمديرين فقط. في **المجموعات** اختر الأدوار في المربّع الأيسر وانقلها إلى المربّع الأيمن بالسهم '
                 '(النقر المزدوج يعمل أيضاً). اترك **صلاحيات المستخدم** فارغة.', 'adm_24_add_user_permissions.png', 'المجموعات المختارة لحساب إدخال بيانات في مركز'),
                ('اضغط **حفظ**. تُعاد القائمة مع رسالة تأكيد. سلّم بيانات الدخول للمستخدم عبر قناة آمنة واطلب منه تغيير كلمة المرور عند أول دخول.',
                 'adm_25_add_user_done.png', 'تم حفظ الحساب'),
            ]),
            ('table', ['قاعدة كلمة المرور', 'المتطلّب'], [
                ['الطول', '8 أحرف على الأقل'],
                ['الأرقام', '3 أرقام على الأقل'],
                ['الأحرف', 'حرف كبير وحرف صغير على الأقل'],
                ['الرموز', 'رمز واحد على الأقل مثل ! @ # $ % & *'],
                ['غير شائعة', 'ليست كلمة شائعة ولا تشبه اسم المستخدم'],
            ]),
        ]},
        # 5 -----------------------------------------------------------------
        {'title': 'وصفات الأدوار', 'body': [
            ('p', 'استخدم هذه التركيبات عند إنشاء الحسابات. يجب أن تتطابق أسماء المجموعات تماماً.'),
            ('table', ['نوع الحساب', 'المجموعات', 'الارتباط', 'علامات الحالة'], [
                ['إدخال بيانات مركز التعليم غير النظامي', '`MSCC`، `MSCC_CENTER` (+ `EXPORT` للسماح بالتحميل)', 'المركز والشريك', 'نشط'],
                ['منسّق الشريك', '`MSCC_PARTNER`', 'الشريك', 'نشط'],
                ['قارئ على مستوى القطاع (اليونيسف / الوزارة)', '`MSCC_UNICEF`', 'لا شيء', 'نشط'],
                ['قائمة المستفيدين على مستوى القطاع', '`MSCC`، `MSCC_CENTER`، `MSCC_FULL`', 'المركز والشريك', 'نشط'],
                ['نقطة اتصال مدرسة ALP', '`ALP_SCHOOL`', 'المدرسة', 'نشط'],
                ['موظفو الجسر (CLM)', '`CLM_Bridging` (+ `CLM_BRIDGING_ALL`، `CLM_TEACHER`، `CLM_ATTENDANCE` بحسب الحاجة)', 'بحسب تعليمات فريق CLM', 'نشط'],
                ['مدير النظام', 'لا يلزم', 'لا شيء', 'نشط، صفة موظف، مستخدم خارق'],
                ['مدير محدود (مثلاً إدارة المستخدمين فقط)', 'لا يلزم', 'لا شيء', 'نشط، صفة موظف + صلاحيات النماذج (القسم 10)'],
            ]),
            ('h3', 'مثال: نقطة اتصال مدرسة ALP'),
            ('steps', [
                ('في تبويبة **المعلومات الشخصية** اكتب اسم المدرسة في حقل **المدرسة** واخترها من الاقتراحات. لا تعرض القائمة إلا المدارس المفتوحة.',
                 'adm_32_school_autocomplete.png', 'اختيار مدرسة حساب ALP'),
                ('تظهر المدرسة المختارة في الحقل. يرتبط كل حساب بمدرسة واحدة بالضبط.', 'adm_30_alp_user_personal_info.png', 'حساب ALP مع مدرسته'),
                ('في تبويبة **الصلاحيات** المجموعة الوحيدة المطلوبة هي `ALP_SCHOOL`.', 'adm_31_alp_user_permissions.png', 'مجموعات حساب ALP'),
            ]),
        ]},
        # 6 -----------------------------------------------------------------
        {'title': 'تعديل حساب', 'body': [
            ('steps', [
                ('افتح المستخدم من القائمة (اضغط اسم المستخدم). غيّر القيم في تبويبات **الحساب** أو **المعلومات الشخصية** أو **الصلاحيات** واضغط **حفظ**، أو **حفظ ومتابعة التعديل** للبقاء في الصفحة.',
                 'adm_22_add_user_saved.png', 'نموذج المستخدم'),
                ('عندما ينتقل موظف إلى مركز أو مدرسة أخرى، حدّث **الارتباط** و**المجموعات** معاً، ثم اطلب من المستخدم تسجيل الخروج والدخول مجدداً.', None, None),
                ('**السجل** (الأزرار الجانبية) يعرض كل تغيير أُجري على الحساب من لوحة الإدارة مع التاريخ والمدير الذي أجراه.', 'adm_62_user_history.png', 'سجل تغييرات حساب'),
            ]),
            ('note', 'لا تُعد استخدام حساب قديم لشخص جديد: أنشئ حساباً جديداً وعطّل القديم، لتبقى السجلات التي أنشأها كل شخص قابلة للتتبّع.'),
        ]},
        # 7 -----------------------------------------------------------------
        {'title': 'إعادة تعيين كلمة المرور', 'body': [
            ('p', 'لا توجد إعادة تعيين ذاتية لكلمة المرور في التطبيق: يتواصل المستخدمون الذين نسوا كلمة المرور مع المدير.'),
            ('steps', [
                ('افتح المستخدم واضغط **إعادة تعيين كلمة المرور** في تبويبة **الحساب** (تحت بصمة كلمة المرور).', 'adm_40_reset_password_empty.png', 'نموذج إعادة تعيين كلمة المرور'),
                ('أدخل كلمة المرور الجديدة مرتين. يجب أن تتّبع قواعد كلمة المرور في القسم 5.', 'adm_41_reset_password_filled.png', 'كلمة المرور الجديدة بعد الإدخال'),
                ('اضغط **تغيير كلمة المرور**. يظهر تأكيد؛ أبلغ كلمة المرور بشكل آمن واطلب من المستخدم تغييرها بعد الدخول.', 'adm_42_reset_password_done.png', 'تم تغيير كلمة المرور'),
            ]),
            ('note', 'بعد خمس محاولات دخول فاشلة خلال خمس دقائق يُقفل الحساب مؤقتاً. يُرفع القفل تلقائياً بعد بضع دقائق؛ لا يلزم إعادة تعيين كلمة المرور.'),
        ]},
        # 8 -----------------------------------------------------------------
        {'title': 'تعطيل الحسابات وإعادة تفعيلها وحذفها', 'body': [
            ('p', '**عطّل** حسابات من يغادرون؛ لا تحذفها. الحساب المعطَّل لا يستطيع الدخول، لكن التسجيلات والحضور والتصديرات التي أنشأها تحتفظ بمؤلّفها.'),
            ('steps', [
                ('في قائمة المستخدمين علّم الحسابات، اختر **تعطيل** من قائمة الإجراءات واضغط **تنفيذ**. لإعادة التفعيل استخدم **تفعيل**. يمكنك أيضاً إلغاء تعليم **نشط** في تبويبة الصلاحيات لمستخدم واحد.',
                 'adm_50_action_disable.png', 'الإجراء الجماعي "تعطيل"'),
                ('يعرض عمود **نشط** أيقونة حمراء للحسابات المعطَّلة. استخدم فلتر **نشط** لعرضها.', 'adm_51_user_disabled.png', 'حساب معطَّل'),
                ('**حذف** (الزر الأحمر في نموذج المستخدم، أو إجراء **حذف المستخدمين المحدّدين**) يعرض أولاً صفحة تأكيد تسرد كل ما سيُزال مع الحساب. لا يمكن التراجع عن الحذف؛ '
                 'احتفظ به للحسابات التي أُنشئت خطأً ولم تُدخل بيانات قط.', 'adm_52_delete_user_confirm.png', 'صفحة تأكيد الحذف'),
            ]),
        ]},
        # 9 -----------------------------------------------------------------
        {'title': 'المجموعات والصلاحيات', 'body': [
            ('p', 'تُدار المجموعات تحت **المصادقة والتفويض ← المجموعات** (يمكن الوصول إليها من بحث لوحة التحكّم أو العنوان `/admin/auth/group/`).'),
            ('steps', [
                ('تعرض القائمة المجموعات الموجودة. يتعرّف التطبيق على الأسماء الواردة في القسم 2؛ المجموعة بأي اسم آخر لا أثر لها في التطبيق.', 'adm_60_groups_list.png', 'قائمة المجموعات'),
                ('فتح مجموعة يعرض **صلاحيات النماذج** الخاصة بها (إضافة / تعديل / حذف / عرض لكل جدول). تهمّ هذه الصلاحيات فقط حسابات الموظفين التي تستخدم لوحة الإدارة من دون صفة المستخدم الخارق. '
                 'تعمل أدوار القسم 2 من دون أي صلاحية نموذج.', 'adm_61_group_change.png', 'مجموعة وصلاحيات نماذجها'),
            ]),
            ('h3', 'منح شخص صلاحية إدارة محدودة'),
            ('bullets', [
                'علّم **صفة موظف** (وليس مستخدم خارق) على المستخدم.',
                'أنشئ مجموعة مثل `ADMIN_USERS` بالصلاحيات **عرض مستخدم**، **تعديل مستخدم**، **إضافة مستخدم** وأضف المستخدم إليها، أو انقل الصلاحيات نفسها إلى مربّع **صلاحيات المستخدم** الخاص به.',
                'يرى الشخص عندها جدول المستخدمين فقط في لوحة الإدارة. افعل الشيء نفسه بصلاحيات المراكز أو المدارس أو الدورات لمديري البيانات المرجعية.',
            ]),
            ('note', 'لا تمنح أبداً **صفة المستخدم الخارق** لحساب يُستخدم لإدخال البيانات اليومي، وأبقِ عدد المستخدمين الخارقين صغيراً.'),
        ]},
        # 10 ----------------------------------------------------------------
        {'title': 'البيانات المرجعية', 'body': [
            ('p', 'تغذّي القوائم أدناه القوائم المنسدلة في التطبيق. أضف أو صحّح المدخلات هنا؛ لا تحذف مدخلات مستخدمة في تسجيلات موجودة.'),
            ('steps', [
                ('**المدارس ← المنظمات الشريكة**: الشركاء المنفّذون. يجب أن يوجد الشريك قبل ربط المراكز والحسابات به.', 'adm_70_partners.png', 'المنظمات الشريكة'),
                ('يحتوي نموذج الشريك على الاسم المختصر ونقاط الاتصال (المتابعة والتقييم، مدير البرنامج).', 'adm_71_partner_change.png', 'نموذج المنظمة الشريكة'),
                ('**المواقع ← المراكز**: مراكز التعليم غير النظامي مع الشريك والنوع والمحافظة والقضاء والمنطقة العقارية.', 'adm_72_centers.png', 'المراكز'),
                ('يسجّل نموذج المركز أيضاً المدير والهاتف والإحداثيات (تستخدمها خريطة المراكز) وإمكانية الوصول والحزم المقدَّمة.', 'adm_73_center_change.png', 'نموذج المركز'),
                ('**المدارس ← المدارس**: المدارس الرسمية لوحدة ALP. يرتبط كل حساب ALP بإحداها؛ لا تُعرض المدارس المغلقة عند ربط الحسابات.', 'adm_74_schools.png', 'المدارس'),
                ('نموذج المدرسة: رقم المركز التربوي، الاسم، النوع، الدوام، بيانات الاتصال، الموقع والخدمات. تصون نقاط اتصال المدارس معظمه بأنفسها من التطبيق.', 'adm_75_school_change.png', 'نموذج المدرسة'),
                ('**بيانات التعليم غير النظامي ← الدورات**: دورات البرنامج (السنوات). علّم **السنة الحالية** على الدورة (الدورات) المفتوحة للتسجيل: لا تُعرض في نماذج الالتحاق والحضور إلا الدورات الحالية.',
                 'adm_76_rounds.png', 'الدورات'),
                ('للدورة اسم وسنة وعلامة السنة الحالية. أنشئ الدورة الجديدة قبل بداية السنة وألغِ تعليم الدورة السابقة عند إقفالها.', 'adm_77_round_change.png', 'نموذج الدورة'),
                ('**ALP ← دورات ALP** و**برامج ALP**: السنوات الدراسية ومستويات البرنامج المعروضة في تسجيل ALP.', 'adm_78_alp_rounds.png', 'دورات ALP'),
                ('**ALP ← تعريفات درجات ALP**: سطر لكل مادة مع الحدّ الأدنى والأقصى للدرجة. يُبنى نموذج الدرجات في ALP من هذه القائمة.', 'adm_80_alp_grading_definitions.png', 'تعريفات درجات ALP'),
                ('**بيانات التعليم غير النظامي ← الحزم**: البرامج التعليمية مع الفئة العمرية التي تقبلها. لا يرى الطفل إلا البرامج التي يشمل نطاقها العمري عمره؛ تعرض صفحة الحضور حزم فئة "Education".',
                 'adm_81_packages.png', 'الحزم'),
                ('**إعدادات بيانات الطفل ← الجنسيات، أنواع الهوية، أنواع المرفقات، مواضيع تدريب المعلّمين** و**المدارس ← المستويات التعليمية**: قيم القوائم في نماذج التسجيل والمعلّمين.',
                 'adm_82_nationalities.png', 'الجنسيات'),
                ('**المواقع ← المواقع**: التسلسل محافظة / قضاء / منطقة عقارية (أنواع المواقع 1 و2 و3). أبقِ الأسماء العربية والإنكليزية معبّأة؛ تُطابَق مع قائمة قرى الامتحان.',
                 'adm_83_locations.png', 'المواقع'),
            ]),
        ]},
        # 11 ----------------------------------------------------------------
        {'title': 'المراقبة', 'body': [
            ('steps', [
                ('**المراقبة ← نشاط المستخدمين** يسجّل من فعل ماذا ومتى في التطبيق. صفِّ بحسب المستخدم أو التاريخ عند التحقيق في مسألة.', 'adm_90_user_activity.png', 'سجل نشاط المستخدمين'),
                ('**المراقبة ← سجل التصدير** يعرض كل تصدير طُلب وحالته وملفه. تظهر هنا عمليات التصدير الفاشلة.', 'adm_91_export_history.png', 'سجل التصدير'),
                ('**إعدادات Celery ← سجلات تشغيل المهام** يعرض المهام الخلفية (التصدير، المهام المجدولة) ونتائجها.', 'adm_92_task_logs.png', 'سجلات تشغيل المهام'),
                ('**بيانات التعليم غير النظامي ← التسجيلات** و**الطفل ← الأطفال** يتيحان الوصول المباشر إلى السجلات. استخدمهما للتصحيحات التي لا يسمح بها التطبيق (مثلاً إلغاء تسجيل) وبعد التحقّق مع المركز فقط.',
                 'adm_93_registrations.png', 'التسجيلات في لوحة الإدارة'),
            ]),
        ]},
        # 12 ----------------------------------------------------------------
        {'title': 'ممارسات جيدة', 'body': [
            ('bullets', [
                '**شخص واحد، حساب واحد.** لا تشارك بيانات الدخول بين الموظفين؛ أنشئ حساباً منفصلاً لكل شخص.',
                '**الحدّ الأدنى من الصلاحيات.** امنح فقط المجموعات والارتباط التي يحتاجها الشخص. تجنّب `MSCC_FULL` وصفة المستخدم الخارق ما لم تكن مطلوبة.',
                '**راجع الحسابات بانتظام.** صدّر قائمة المستخدمين كل ثلاثة أشهر، وعطّل المغادرين، وتحقّق من الارتباطات.',
                '**عطّل ولا تحذف** للحفاظ على مسار التدقيق.',
                '**أمّن بيانات الدخول.** أرسل كلمات المرور الأولية عبر قناة آمنة واطلب تغييرها عند أول دخول.',
                '**سجّل الخروج** من لوحة الإدارة عند مغادرة الحاسوب؛ تنتهي الجلسة أيضاً تلقائياً بعد فترة من عدم النشاط.',
            ]),
        ]},
        # 13 ----------------------------------------------------------------
        {'title': 'الأسئلة الشائعة', 'body': [
            ('table', ['السؤال', 'الجواب'], [
                ['يسجّل المستخدم الدخول لكن كل القوائم فارغة.', 'الارتباط ناقص: حدّد المركز (والشريك) أو المدرسة في تبويبة المعلومات الشخصية بما يتوافق مع المجموعات.'],
                ['يتلقّى المستخدم "403 / غير مسموح" في صفحة.', 'يفتقر الحساب إلى المجموعة التي تفتح تلك الصفحة. قارن بوصفات الأدوار في القسم 6.'],
                ['لا يستطيع المستخدم فتح لوحة الإدارة.', 'علّم صفة موظف، وامنح صلاحيات النماذج أو صفة المستخدم الخارق (القسم 10).'],
                ['لا يستطيع المستخدم الخارق إضافة تسجيل ALP.', 'هذا مقصود: تُدخل بيانات ALP من حسابات المدارس فقط.'],
                ['أي دورة تُعرض في النماذج؟', 'الدورات التي تحمل علامة السنة الحالية فقط (NFE) أو دورة ALP الحالية.'],
                ['برنامج غير موجود في تسجيل الطفل.', 'تحقّق من النطاق العمري للحزمة وتاريخ ولادة الطفل.'],
                ['هل يمكنني إعادة تسمية مجموعة؟', 'لا. يتحقّق التطبيق من الأسماء بالضبط؛ إعادة تسمية مجموعة تزيل صلاحيات جميع أعضائها.'],
                ['كيف أعرف من عدّل سجلاً؟', 'افتح السجل واضغط السجل (History)، أو راجع سجل نشاط المستخدمين.'],
            ]),
        ]},
    ],
}

MANUALS = {'en': EN, 'ar': AR}
