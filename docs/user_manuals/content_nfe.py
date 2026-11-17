# -*- coding: utf-8 -*-
# flake8: noqa
"""Content of the NFE module user manual (English and Arabic).

Screenshots are referenced by file name inside ``screenshots/<lang>/``.
"""

EN = {
    'title': 'NFE Module – User Manual',
    'subtitle': 'BMA Platform – Non-Formal Education Sector',
    'audience': 'For center staff, partner organisation staff and coordinators',
    'intro': [
        'This manual explains, step by step, how to use the **NFE (Non-Formal Education) module** of the BMA '
        'platform. It is written for center staff who register children, record the services they receive, '
        'track daily attendance, manage teachers and consult the dashboards. No technical knowledge is required.',
        'Each step is illustrated with a screenshot taken from the system. Screens may differ slightly depending '
        'on your role: a **center user** sees only the children of their own center, a **partner user** sees all '
        'the centers of their organisation, and **UNICEF users** have a read-only view across all partners.',
        'The data shown in the screenshots is demonstration data only.',
    ],
    'sections': [
        # 1 -----------------------------------------------------------------
        {'title': 'Getting Started – Login and Navigation', 'body': [
            ('p', 'Open Google Chrome or Mozilla Firefox and go to the platform address given to you by your '
                  'coordinator. Accounts are created by the system administrator; there is no self-registration.'),
            ('steps', [
                ('Open the login page. Enter your **username** and **password**.', '00_login_empty.png', 'The login page'),
                ('Click **Sign in**. If the details are correct you are taken to your home page.', '00_login_filled.png', 'Login form with the credentials filled in'),
                ('The **home page** shows today\'s registrations, this week\'s registrations, the centers reporting, '
                 'the average attendance, a 14-day registration trend and your recent data exports. The **New '
                 'Registration** card opens the registration form directly.', 'nfe_01_home.png', 'The home page after login'),
                ('To change the interface language, click the **globe icon** in the top bar and choose '
                 '**English** or **العربية**. The page reloads in the chosen language with a right-to-left layout for Arabic.',
                 'nfe_02_language_menu.png', 'Language menu'),
                ('Click your **name** in the top-right corner to open the user menu: **Profile**, **Change Password** and **Logout**.',
                 'nfe_03_user_menu.png', 'User menu'),
            ]),
            ('h3', 'The side menu'),
            ('table', ['Menu entry', 'What it opens'], [
                ['Home', 'The home page with the daily summary cards'],
                ['Dashboard', 'The NFE operational dashboard (registrations, gender, nationality, age groups…)'],
                ['Registration', 'The beneficiary list, the registration form and the child profiles'],
                ['Attendance', 'Daily attendance entry for your center'],
                ['Centers', 'The list of centers you can access'],
                ['Teachers', 'The teacher list and the teacher form'],
                ['Pivot Builder', 'Build your own cross-tabulations of the registration data'],
                ['Learning Outcome', 'Learning outcome and socio-economic analysis'],
                ['Teacher Dashboard', 'Teacher demographics, assignments and training'],
                ['Attendance Heatmap', 'Attendance patterns across the year'],
                ['Centers Map', 'Map and profile of the centers'],
                ['User Guide', 'The documentation inside the system'],
            ]),
            ('note', 'For security, the system logs you out automatically after a period of inactivity. Save your work regularly. '
                     'After five failed login attempts in five minutes the account is temporarily blocked: wait a few minutes and try again.'),
        ]},
        # 2 -----------------------------------------------------------------
        {'title': 'The Beneficiary List', 'body': [
            ('p', 'The beneficiary list shows every child registered in your center (or in all the centers of your partner '
                  'organisation). Open it with **Registration** in the side menu.'),
            ('steps', [
                ('The list shows one row per registration: round, unique ID, names, gender, age, birthday, nationality and '
                 'programme. Click a column header to sort by that column. Scroll horizontally to see all the columns.',
                 'nfe_10_list.png', 'The beneficiary list'),
                ('Click **Search** to open the filter panel. Filter by first, father, last or mother name, unique ID, gender, '
                 'nationality, round or programme, then click **Apply Filters**. **Clear All** removes the filters.',
                 'nfe_11_list_search.png', 'The search and filter panel'),
                ('Click **Actions** on a row to open the row menu: **View Profile**, **Upload Photo**, **Edit Information** and '
                 '**Delete Record**. Deleting asks for a confirmation and cannot be undone.',
                 'nfe_12_list_actions.png', 'The Actions menu of a registration'),
            ]),
            ('note', 'The **Total absence** column counts the days the child was marked absent in the current round. '
                     'It is a quick way to spot children at risk of dropping out.'),
        ]},
        # 3 -----------------------------------------------------------------
        {'title': 'Registering a New Child', 'body': [
            ('p', 'Registration is done through a **3-step wizard**: Identity, Caregivers and Review. The child is only '
                  'saved when you click **Complete Registration** on the last step. Fields marked with a red asterisk (*) are mandatory.'),
            ('p', 'Open the form with **New Registration** on the home page, or from the beneficiary list.'),
            ('h3', 'Before you start: avoid duplicates'),
            ('p', 'As soon as you type the child\'s name and date of birth, the **Potential Matches** panel at the top of the '
                  'form searches the existing records. If the same child is already registered, the panel turns red, shows the '
                  'existing record and blocks the **Next Step** button. In that case do **not** create a new record: open the existing '
                  'profile, or use **Select & Re-register** to add the child to a new round.'),
            ('img', 'nfe_21_reg_duplicate_warning.png', 'The duplicate check runs while you type the identity'),
            ('h3', 'Step 1 – Identity'),
            ('steps', [
                ('Fill in the **Basic Identity Information**: child photo (optional), first name, father\'s name, family name, '
                 'date of birth (day, month, year), country and place of birth, gender, mother\'s full name, nationality and the '
                 '**non-formal education programme** (BLN Level 1, 2 or 3). Names must be written in **Arabic letters** exactly as on the official document.',
                 'nfe_20_reg_step1_empty.png', 'Step 1 – the empty identity form'),
                ('Fill in the **Residential Address**: governorate, district, cadaster and village. Each list is loaded after you '
                 'choose the previous level. Then answer the **disability** question in **Status & Background**.', None, None),
                ('Check the data and click **Next Step**. If a mandatory field is missing, the field is highlighted in red and a '
                 '**Verification Required** message lists what must be corrected.',
                 'nfe_22_reg_step1_filled.png', 'Step 1 completed'),
            ]),
            ('table', ['Field', 'Guidance'], [
                ['First / Father / Family name', 'In Arabic letters, as written on the ID document'],
                ['Date of birth', 'Select day, month and year from the lists'],
                ['Country and place of birth', 'As written on the official document'],
                ['Mother full name', 'Required, in Arabic letters'],
                ['Nationality', 'Choose from the list; if "Other" specify it in the next field'],
                ['Non-formal education programme', 'BLN Level 1, BLN Level 2 or BLN Level 3'],
                ['Formal education unique student ID', 'Optional – the ID used in the formal school, if any'],
                ['Governorate / District / Cadaster / Village', 'Where the child currently lives'],
                ['Disability or special need', 'Required; if "Other" describe it'],
            ]),
            ('h3', 'Step 2 – Caregivers'),
            ('steps', [
                ('Enter the **primary phone number** of the caregiver in the format **XX-XXXXXX** (for example 03-123456). '
                 'This is the number the center uses to contact the family.', 'nfe_23_reg_step2_empty.png', 'Step 2 – caregiver contact'),
                ('Click **Next Step**. Use **Previous** at any time to go back and correct a value.',
                 'nfe_24_reg_step2_filled.png', 'Step 2 completed'),
            ]),
            ('h3', 'Step 3 – Review and submit'),
            ('steps', [
                ('Review the summary: full name, date of birth, country and place of birth, nationality, gender, phone number, '
                 'programme and address. If anything is wrong click **Previous** and correct it. **Reset Form** clears everything.',
                 'nfe_25_reg_step3_review.png', 'Step 3 – final review'),
                ('Click **Complete Registration**. The message "Your data has been sent successfully to the server" confirms the '
                 'registration and the child\'s **profile page** opens.', 'nfe_26_reg_submitted.png', 'The profile page right after registration'),
            ]),
            ('note', 'The center, partner and round are filled in automatically from your account. If your account has no center '
                     'assigned, a warning is displayed on the list: ask your administrator to link your account to a center.'),
        ]},
        # 4 -----------------------------------------------------------------
        {'title': 'The Child Profile', 'body': [
            ('p', 'The profile is the central record of a child. Open it from the beneficiary list with **Actions → View Profile**.'),
            ('steps', [
                ('The **header** shows the photo, the full name, the unique ID, the date of birth with the age, the address, the partner, '
                 'the center and the current round. The buttons on the right open **Download Examination Card (Word)** and **Edit Profile**.',
                 'nfe_30_profile_header.png', 'Profile header'),
                ('The **Personal Info** tab groups the core identity, the household and care information and the social and economic situation.',
                 'nfe_30_profile_full.png', 'Personal Info tab'),
                ('The **Education situation** tab shows the current enrolment (educational level, programme, round, section, registration '
                 'date), the education history, the pre/post grading of the programme and the referral card.',
                 'nfe_31_profile_education_tab.png', 'Education situation tab'),
                ('The **Attendances** tab shows the total teaching days, the days attended, the absences and the absences of the current '
                 'month. Click a month in **Monthly History** to see the detailed daily records.',
                 'nfe_32_profile_attendance_tab.png', 'Attendances tab'),
                ('The **Exceptional Exam** tab shows the exam details recorded for the registration, or a button to add them (see section 6).',
                 'nfe_33_profile_exam_tab.png', 'Exceptional Exam tab'),
            ]),
            ('h3', 'Editing the profile'),
            ('steps', [
                ('Click **Edit Profile** (or **Actions → Edit Information** in the list). The same 3-step form opens with the saved values. '
                 'Change what is needed, go through the steps and click **Complete Registration** to save.',
                 'nfe_62_edit_profile.png', 'Editing a registration'),
            ]),
            ('h3', 'Uploading the child photo'),
            ('steps', [
                ('Click the **camera icon** on the profile photo, or **Actions → Upload Photo** in the list. Choose a clear, recent photo '
                 'of the child (JPG or PNG) and click **Save**.', 'nfe_60_photo_upload.png', 'Photo upload form'),
                ('The profile reopens with the new photo. The photo is also embedded in the Excel export and printed on the examination card.',
                 'nfe_61_photo_saved.png', 'Photo saved'),
            ]),
            ('h3', 'Examination card'),
            ('p', 'Click **Download Examination Card (Word)** in the profile header to download an editable Word card with the '
                  'child\'s photo, round, registration ID, partner, full name, date of birth, nationality and governorate. '
                  'Correct the profile first if anything is wrong: each download reads the saved record again.'),
        ]},
        # 5 -----------------------------------------------------------------
        {'title': 'Education Situation and Round Enrolment', 'body': [
            ('p', 'The **education situation** records the child\'s educational level at registration and the programme, round and class '
                  'section the child attends. It is required before the child appears in the attendance sheets.'),
            ('steps', [
                ('Open the profile, go to the **Education situation** tab and click **Add** (or **Edit** if a situation already exists).',
                 'nfe_40_education_form_empty.png', 'The education situation form'),
                ('Choose the **educational level when registering**, the **round**, the **programme**, the **class section** and the '
                 '**date of registration in the round**. If the child dropped out of a school, give the dropout date.',
                 'nfe_41_education_form_filled.png', 'Education situation completed'),
                ('Click **Save Education Data**. The profile reopens on the Education situation tab with the new enrolment and a new line '
                 'in the **Education History**.', 'nfe_42_education_saved.png', 'The saved education situation'),
            ]),
            ('h3', 'Registering the child in a new round'),
            ('steps', [
                ('When a new round starts, open the **Register in a New Round** page for the child (from the duplicate warning\'s '
                 '**Select & Re-register** button, or from the **New Round** button in the profile header when your role has it). '
                 'The **Registration History** lists the rounds the child already attended.',
                 'nfe_34_new_round_form.png', 'Register in a new round'),
                ('Fill in the education situation for the new round and click **Save Education Data**. A new registration record is created '
                 'for the current round; the previous rounds stay in the history.', None, None),
            ]),
            ('note', 'The programmes offered depend on the child\'s age. If the programme you need is not listed, check the date of birth.'),
        ]},
        # 6 -----------------------------------------------------------------
        {'title': 'Exceptional Exam', 'body': [
            ('p', 'Children who sit the exceptional examination need an exam record on their registration. Each registration has one exam record.'),
            ('steps', [
                ('Open the profile, go to the **Exceptional Exam** tab and click **Add Exceptional Exam**. The residence, country and place of '
                 'birth and the programme are taken from the registration and displayed in grey.',
                 'nfe_50_exam_form_empty.png', 'The exceptional exam form'),
                ('Check the **grade applying for the examination** (derived from the programme level), choose the **mathematics examination '
                 'language** (Arabic, English or French) and the **language examination** (English or French).',
                 'nfe_51_exam_form_filled.png', 'Exam form completed'),
                ('Click **Save**. The message "Exceptional exam saved" appears and the tab shows the recorded answers. Use **Edit Exceptional '
                 'Exam** to correct them later.', 'nfe_52_exam_saved.png', 'The saved exam details'),
            ]),
            ('note', 'If the residence or programme shown is wrong, correct the child\'s registration first (Edit Profile) and then come back to the exam form.'),
        ]},
        # 7 -----------------------------------------------------------------
        {'title': 'Daily Attendance', 'body': [
            ('p', 'Attendance is recorded per day, per programme and per class section. Open it with **Attendance** in the side menu.'),
            ('steps', [
                ('The date defaults to **today**. Choose the **Education Program**, the **Round** and the **Section**.',
                 'nfe_70_attendance_page.png', 'The attendance page'),
                ('Click **Load**. The children enrolled in that programme and section appear on the right, each with **Attended** and **Absent** buttons.',
                 'nfe_71_attendance_loaded.png', 'Children loaded for the selected class'),
                ('Children are marked **Attended** by default. For each absent child click **Absent** and choose the **absence reason** '
                 '(Sick, Transportation or Other – describe it in the text box).', 'nfe_72_attendance_marked.png', 'Absences marked with their reason'),
                ('Click **Save**. A **Success** message confirms the attendance was saved. You can reload the same day later to correct it.',
                 'nfe_73_attendance_saved.png', 'Attendance saved'),
                ('If the center was closed, select **Day Off** instead of marking children, choose the **closing reason** and save.',
                 'nfe_74_attendance_day_off.png', 'Recording a day off'),
            ]),
            ('bullets', [
                'Attendance can be recorded for today or for a past date; **future dates are refused**.',
                'A child who does not appear in the list has no education situation for that programme and section (see section 5), or the registration is not active.',
                '**Download** gives a CSV file of the list currently loaded on screen.',
            ]),
        ]},
        # 8 -----------------------------------------------------------------
        {'title': 'Teachers', 'body': [
            ('p', 'Every teacher or facilitator of the center must be recorded. Open **Teachers** in the side menu.'),
            ('steps', [
                ('The teacher list shows the names, gender, phone number, center, round and who created the record. Use **Search** to filter '
                 'and **Export** to download the list. Click **Add Teacher** to create a record.', 'nfe_80_teachers_list.png', 'The teacher list'),
                ('Fill in **Identity & Contact**: names in Arabic letters, gender, birth date, nationality, ID type and number, phone '
                 '(format XX-XXXXXX) and email.', 'nfe_81_teacher_form_empty.png', 'The teacher form'),
                ('Fill in **Assignment & Qualifications**: center, academic year, assignment, teaching hours, subjects provided, grade levels, '
                 'training topics attended, years of experience and extra coaching. Add up to four supporting documents under **Required Documents**.',
                 'nfe_82_teacher_form_filled.png', 'Teacher form completed'),
                ('Click **Complete Registration**. The teacher appears in the list.', 'nfe_83_teacher_saved.png', 'Teacher saved'),
                ('To update a teacher use **Actions → Edit** in the list, change the values and save. **Delete** removes the teacher after confirmation.',
                 'nfe_84_teacher_edit.png', 'Editing a teacher'),
            ]),
        ]},
        # 9 -----------------------------------------------------------------
        {'title': 'Centers', 'body': [
            ('steps', [
                ('**Centers** in the side menu lists the centers you can access with their partner, type and location. Center users see their own '
                 'center; partner users see all the centers of their organisation. Use the row actions to open or update a center profile '
                 '(name, type, address, GPS coordinates, services provided).', 'nfe_85_centers_list.png', 'The center list'),
            ]),
        ]},
        # 10 ----------------------------------------------------------------
        {'title': 'Exporting Data', 'body': [
            ('p', 'Exports are started from the beneficiary list and prepared in the background, so you can keep working.'),
            ('steps', [
                ('In the beneficiary list click **Export**. Choose the **children to export** (all the children you can access, or only the current '
                 'filter results) and the **format**: CSV (text only), Excel with photographs, or Word examination cards (ZIP).',
                 'nfe_13_export_modal.png', 'Export options'),
                ('Click **Start Export**. When the file is ready a message tells you the download starts automatically.',
                 'nfe_14_export_started.png', 'Export completed'),
                ('Click the **bell icon** in the top bar to open **Recent Exports**. Each entry shows its status and lets you download the file again. '
                 '**View All History** opens the full export history.', 'nfe_15_export_history.png', 'Recent exports menu'),
            ]),
            ('bullets', [
                'Excel exports embed each child photo in the same row as the child and registration IDs.',
                'CSV files are UTF-8 with a byte-order mark, so Arabic names open correctly in Excel.',
                'Only the user who requested an export can download it.',
                '**Download Examination Cards** on the list prepares the Word cards of the selected children as one ZIP file.',
            ]),
        ]},
        # 11 ----------------------------------------------------------------
        {'title': 'Dashboards and Analytics', 'body': [
            ('p', 'The **Analytics** entries of the side menu give an overview of your data. All dashboards are limited to the centers you can access.'),
            ('steps', [
                ('**Dashboard** – total registrations, active centers, partners and rounds, followed by charts on gender, age groups, nationality, '
                 'source of identification, registrations per round, family status, disability, cash support and children moved between rounds. '
                 'Use **Filters** to narrow the data.', 'nfe_90_dashboard.png', 'The operational dashboard'),
                ('**Learning Outcome** – attendance rate, child labour rate, transition to formal education, grade improvement and dropout, with '
                 'socio-economic and impact charts.', 'nfe_91_learning_outcome.png', 'Learning outcome analysis'),
                ('**Teacher Dashboard** – number of teachers, gender, nationality, assignments, subjects and training.',
                 'nfe_92_teacher_dashboard.png', 'Teacher dashboard'),
                ('**Attendance Heatmap** – one square per day coloured by the attendance rate, overall and per programme. Dark green is high '
                 'attendance; light squares show days to check.', 'nfe_93_attendance_heatmap.png', 'Attendance heatmap'),
                ('**Centers Map** – the centers on a map with their characteristics and the list of registered children. Filter by partner and center.',
                 'nfe_94_centers_map.png', 'Centers map'),
                ('**Pivot Builder** – drag the fields (center, district, gender, governorate, nationality, partner, programme…) into rows and columns '
                 'to build your own table or chart; choose the aggregation (count, sum…) in the list on the left.',
                 'nfe_95_pivot_builder.png', 'Pivot builder'),
            ]),
        ]},
        # 12 ----------------------------------------------------------------
        {'title': 'Your Account', 'body': [
            ('steps', [
                ('**Profile** (user menu) shows your partner organisation, center and the information linked to your account. '
                 'Contact the administrator to change these assignments.', 'nfe_96_profile_page.png', 'Profile page'),
                ('**Change Password** (user menu): enter the current password and the new password twice, then click **Change Password**.',
                 'nfe_97_change_password.png', 'Change password form'),
                ('**Logout** (user menu) ends your session. Always log out when you leave a shared computer.',
                 'nfe_98_logout.png', 'Logout'),
            ]),
            ('table', ['Password rule', 'Requirement'], [
                ['Length', 'At least 8 characters'],
                ['Digits', 'At least 3 digits'],
                ['Letters', 'At least one upper-case and one lower-case letter'],
                ['Symbol', 'At least one symbol such as ! @ # $ % & *'],
                ['Not common', 'Not a common word and not similar to your username'],
            ]),
        ]},
        # 13 ----------------------------------------------------------------
        {'title': 'Frequently Asked Questions', 'body': [
            ('table', ['Question', 'Answer'], [
                ['The Next Step button is disabled on the registration form.', 'A potential duplicate was found. Check the Potential Matches panel: open the existing profile or re-register the child in a new round instead of creating a new record.'],
                ['My names are erased when I leave the field.', 'Names must be written in Arabic letters only. Latin letters and digits are removed automatically.'],
                ['The phone number is refused.', 'Use the format XX-XXXXXX, for example 03-123456.'],
                ['A child does not appear in the attendance list.', 'Add the education situation (programme, round and section) on the child profile, then reload the attendance sheet.'],
                ['The district or village list is empty.', 'Select the governorate first, then the district. If the lists still do not load, click Try again or refresh the page.'],
                ['I cannot see children from another center.', 'Center users only see their own center. Ask your coordinator if you need a wider scope.'],
                ['I forgot my password.', 'There is no self-service reset. Contact your system administrator.'],
                ['Who do I contact for support?', 'Your partner focal point first, then the BMA support team through your coordinator.'],
            ]),
        ]},
    ],
}

AR = {
    'title': 'دليل المستخدم – وحدة التعليم غير النظامي (NFE)',
    'subtitle': 'منصة BMA – قطاع التعليم غير النظامي',
    'audience': 'لموظفي المراكز وموظفي المنظمات الشريكة والمنسّقين',
    'intro': [
        'يشرح هذا الدليل خطوةً بخطوة كيفية استخدام **وحدة التعليم غير النظامي (NFE)** في منصة BMA. وهو موجّه لموظفي '
        'المراكز الذين يسجّلون الأطفال، ويوثّقون الخدمات المقدَّمة لهم، ويتابعون الحضور اليومي، ويديرون بيانات المعلّمين، '
        'ويطّلعون على لوحات المعلومات. لا يتطلّب الدليل أي معرفة تقنية.',
        'كل خطوة مرفقة بلقطة شاشة مأخوذة من النظام. قد تختلف الشاشات قليلاً بحسب دورك: **مستخدم المركز** يرى أطفال مركزه '
        'فقط، و**مستخدم الشريك** يرى جميع مراكز منظمته، و**مستخدمو اليونيسف** لديهم صلاحية اطّلاع فقط على جميع الشركاء.',
        'البيانات الظاهرة في لقطات الشاشة هي بيانات تجريبية فقط.',
    ],
    'sections': [
        # 1 -----------------------------------------------------------------
        {'title': 'البدء – تسجيل الدخول والتنقّل', 'body': [
            ('p', 'افتح متصفّح Google Chrome أو Mozilla Firefox وادخل إلى عنوان المنصة الذي زوّدك به المنسّق. '
                  'يُنشئ مدير النظام الحسابات؛ لا يوجد تسجيل ذاتي.'),
            ('steps', [
                ('افتح صفحة تسجيل الدخول. أدخل **اسم المستخدم** و**كلمة المرور**.', '00_login_empty.png', 'صفحة تسجيل الدخول'),
                ('اضغط **تسجيل الدخول**. إذا كانت البيانات صحيحة تُنقل إلى صفحتك الرئيسية.', '00_login_filled.png', 'نموذج تسجيل الدخول بعد تعبئته'),
                ('تعرض **الصفحة الرئيسية** تسجيلات اليوم، وتسجيلات هذا الأسبوع، والمراكز التي ترسل بيانات، ومعدّل الحضور، '
                 'ومنحنى التسجيلات خلال 14 يوماً، وعمليات تصدير البيانات الأخيرة. بطاقة **تسجيل جديد** تفتح نموذج التسجيل مباشرة.',
                 'nfe_01_home.png', 'الصفحة الرئيسية بعد تسجيل الدخول'),
                ('لتغيير لغة الواجهة اضغط **أيقونة الكرة الأرضية** في الشريط العلوي واختر **العربية** أو **English**. '
                 'تُعاد الصفحة بتحميل اللغة المختارة، مع تخطيط من اليمين إلى اليسار للعربية.',
                 'nfe_02_language_menu.png', 'قائمة اللغة'),
                ('اضغط على **اسمك** في أعلى الصفحة لفتح قائمة المستخدم: **الملف الشخصي**، **تغيير كلمة المرور**، **تسجيل الخروج**.',
                 'nfe_03_user_menu.png', 'قائمة المستخدم'),
            ]),
            ('h3', 'القائمة الجانبية'),
            ('table', ['عنصر القائمة', 'ما يفتحه'], [
                ['المنزل', 'الصفحة الرئيسية مع بطاقات الملخّص اليومي'],
                ['لوحة المعلومات', 'لوحة المعلومات التشغيلية (التسجيلات، الجنس، الجنسية، الفئات العمرية...)'],
                ['التسجيل', 'قائمة المستفيدين ونموذج التسجيل وملفات الأطفال'],
                ['الحضور', 'إدخال الحضور اليومي لمركزك'],
                ['المراكز', 'قائمة المراكز التي يمكنك الوصول إليها'],
                ['المعلّمون', 'قائمة المعلّمين ونموذج المعلّم'],
                ['منشئ الجداول المحورية', 'بناء جداولك المتقاطعة الخاصة من بيانات التسجيل'],
                ['مخرجات التعلّم', 'تحليل مخرجات التعلّم والوضع الاجتماعي والاقتصادي'],
                ['لوحة معلومات المعلّمين', 'بيانات المعلّمين وتكليفاتهم وتدريبهم'],
                ['الخريطة الحرارية للحضور', 'أنماط الحضور على مدار السنة'],
                ['خريطة المراكز', 'خريطة المراكز وملفاتها'],
                ['دليل المستخدم', 'التوثيق داخل النظام'],
            ]),
            ('note', 'لأسباب أمنية يُخرجك النظام تلقائياً بعد فترة من عدم النشاط، لذا احفظ عملك بانتظام. '
                     'بعد خمس محاولات دخول فاشلة خلال خمس دقائق يُقفل الحساب مؤقتاً: انتظر بضع دقائق ثم أعد المحاولة.'),
        ]},
        # 2 -----------------------------------------------------------------
        {'title': 'قائمة المستفيدين', 'body': [
            ('p', 'تعرض قائمة المستفيدين كل طفل مسجّل في مركزك (أو في جميع مراكز منظمتك الشريكة). افتحها من **التسجيل** في القائمة الجانبية.'),
            ('steps', [
                ('تعرض القائمة سطراً لكل تسجيل: الدورة، الرقم الفريد، الأسماء، الجنس، العمر، تاريخ الولادة، الجنسية والبرنامج. '
                 'اضغط على عنوان أي عمود للفرز بحسبه. مرّر أفقياً لرؤية جميع الأعمدة.', 'nfe_10_list.png', 'قائمة المستفيدين'),
                ('اضغط **بحث** لفتح لوحة التصفية. صفِّ بحسب الاسم الأول أو اسم الأب أو اسم العائلة أو اسم الأم، أو الرقم الفريد، أو الجنس، '
                 'أو الجنسية، أو الدورة، أو البرنامج، ثم اضغط **تطبيق الفلاتر**. **مسح الكل** يزيل الفلاتر.',
                 'nfe_11_list_search.png', 'لوحة البحث والتصفية'),
                ('اضغط **الإجراءات** في أي سطر لفتح قائمة السطر: **عرض الملف**، **رفع صورة**، **تعديل المعلومات** و**حذف السجل**. '
                 'يطلب الحذف تأكيداً ولا يمكن التراجع عنه.', 'nfe_12_list_actions.png', 'قائمة الإجراءات الخاصة بتسجيل'),
            ]),
            ('note', 'يعرض عمود **إجمالي الغياب** عدد الأيام التي سُجّل فيها الطفل غائباً في الدورة الحالية، وهو وسيلة سريعة لرصد الأطفال المعرّضين للتسرّب.'),
        ]},
        # 3 -----------------------------------------------------------------
        {'title': 'تسجيل طفل جديد', 'body': [
            ('p', 'يتم التسجيل عبر **معالج من 3 خطوات**: الهوية، مقدّمو الرعاية، المراجعة. لا يُحفظ الطفل إلا عند الضغط على '
                  '**إكمال التسجيل** في الخطوة الأخيرة. الحقول المعلَّمة بنجمة حمراء (*) إلزامية.'),
            ('p', 'افتح النموذج من بطاقة **تسجيل جديد** في الصفحة الرئيسية، أو من قائمة المستفيدين.'),
            ('h3', 'قبل البدء: تجنّب التكرار'),
            ('p', 'بمجرّد كتابة اسم الطفل وتاريخ ولادته، تبحث لوحة **مطابقات محتملة** أعلى النموذج في السجلات الموجودة. '
                  'إذا كان الطفل مسجّلاً سابقاً تتحوّل اللوحة إلى اللون الأحمر وتعرض السجل الموجود وتعطّل زر **الخطوة التالية**. '
                  'في هذه الحالة **لا** تُنشئ سجلاً جديداً: افتح الملف الموجود، أو استخدم **اختيار وإعادة التسجيل** لإضافة الطفل إلى دورة جديدة.'),
            ('img', 'nfe_21_reg_duplicate_warning.png', 'يعمل فحص التكرار أثناء كتابة بيانات الهوية'),
            ('h3', 'الخطوة 1 – الهوية'),
            ('steps', [
                ('املأ **معلومات الهوية الأساسية**: صورة الطفل (اختيارية)، الاسم الأول، اسم الأب، اسم العائلة، تاريخ الولادة (اليوم، الشهر، السنة)، '
                 'بلد ومكان الولادة، الجنس، اسم الأم الكامل، الجنسية و**برنامج التعليم غير النظامي** (BLN المستوى 1 أو 2 أو 3). '
                 'يجب كتابة الأسماء **بالأحرف العربية** كما هي في الوثيقة الرسمية.', 'nfe_20_reg_step1_empty.png', 'الخطوة 1 – نموذج الهوية الفارغ'),
                ('املأ **عنوان السكن**: المحافظة، القضاء، المنطقة العقارية والقرية. تُحمَّل كل قائمة بعد اختيار المستوى السابق. '
                 'ثم أجب عن سؤال **الإعاقة** في قسم الوضع والخلفية.', None, None),
                ('راجع البيانات واضغط **الخطوة التالية**. إذا نقص حقل إلزامي يُظلَّل الحقل بالأحمر وتعرض رسالة **التحقق مطلوب** ما يجب تصحيحه.',
                 'nfe_22_reg_step1_filled.png', 'الخطوة 1 بعد التعبئة'),
            ]),
            ('table', ['الحقل', 'الإرشاد'], [
                ['الاسم الأول / اسم الأب / اسم العائلة', 'بالأحرف العربية كما هي مكتوبة في وثيقة الهوية'],
                ['تاريخ الولادة', 'اختر اليوم والشهر والسنة من القوائم'],
                ['بلد ومكان الولادة', 'كما هو مكتوب في الوثيقة الرسمية'],
                ['اسم الأم الكامل', 'إلزامي، بالأحرف العربية'],
                ['الجنسية', 'اختر من القائمة؛ إذا اخترت "غير ذلك" حدّدها في الحقل التالي'],
                ['برنامج التعليم غير النظامي', 'BLN المستوى 1 أو المستوى 2 أو المستوى 3'],
                ['الرقم الفريد في التعليم النظامي', 'اختياري – الرقم المستخدم في المدرسة الرسمية إن وُجد'],
                ['المحافظة / القضاء / المنطقة العقارية / القرية', 'مكان إقامة الطفل الحالي'],
                ['الإعاقة أو الاحتياج الخاص', 'إلزامي؛ إذا اخترت "غير ذلك" صِفه'],
            ]),
            ('h3', 'الخطوة 2 – مقدّمو الرعاية'),
            ('steps', [
                ('أدخل **رقم الهاتف الأساسي** لمقدّم الرعاية بالصيغة **XX-XXXXXX** (مثلاً 03-123456). هذا هو الرقم الذي يستخدمه المركز للتواصل مع العائلة.',
                 'nfe_23_reg_step2_empty.png', 'الخطوة 2 – بيانات الاتصال بمقدّم الرعاية'),
                ('اضغط **الخطوة التالية**. يمكنك في أي وقت الضغط على **السابق** للرجوع وتصحيح قيمة.', 'nfe_24_reg_step2_filled.png', 'الخطوة 2 بعد التعبئة'),
            ]),
            ('h3', 'الخطوة 3 – المراجعة والإرسال'),
            ('steps', [
                ('راجع الملخّص: الاسم الكامل، تاريخ الولادة، بلد ومكان الولادة، الجنسية، الجنس، رقم الهاتف، البرنامج والعنوان. '
                 'إذا كان هناك خطأ اضغط **السابق** وصحّحه. **إعادة ضبط النموذج** يمسح كل شيء.', 'nfe_25_reg_step3_review.png', 'الخطوة 3 – المراجعة النهائية'),
                ('اضغط **إكمال التسجيل**. تؤكّد رسالة "تم إرسال البيانات بنجاح" التسجيل وتُفتح **صفحة ملف** الطفل.',
                 'nfe_26_reg_submitted.png', 'صفحة الملف مباشرة بعد التسجيل'),
            ]),
            ('note', 'يُملأ المركز والشريك والدورة تلقائياً من حسابك. إذا لم يكن لحسابك مركز مرتبط يظهر تنبيه في القائمة: اطلب من المدير ربط حسابك بمركز.'),
        ]},
        # 4 -----------------------------------------------------------------
        {'title': 'ملف الطفل', 'body': [
            ('p', 'الملف هو السجل المركزي للطفل. افتحه من قائمة المستفيدين عبر **الإجراءات ← عرض الملف**.'),
            ('steps', [
                ('يعرض **رأس الصفحة** الصورة، الاسم الكامل، الرقم الفريد، تاريخ الولادة مع العمر، العنوان، الشريك، المركز والدورة الحالية. '
                 'الأزرار على الجانب تفتح **تحميل بطاقة الامتحان (Word)** و**تعديل الملف**.', 'nfe_30_profile_header.png', 'رأس صفحة الملف'),
                ('تجمع تبويبة **المعلومات الشخصية** الهوية الأساسية، ومعلومات الأسرة والرعاية، والوضع الاجتماعي والاقتصادي.',
                 'nfe_30_profile_full.png', 'تبويبة المعلومات الشخصية'),
                ('تعرض تبويبة **الوضع التعليمي** الالتحاق الحالي (المستوى التعليمي، البرنامج، الدورة، الشعبة، تاريخ التسجيل)، وسجل التعليم، '
                 'وتقييم البرنامج القبلي والبعدي، وبطاقة الإحالة.', 'nfe_31_profile_education_tab.png', 'تبويبة الوضع التعليمي'),
                ('تعرض تبويبة **الحضور** إجمالي أيام التدريس، وأيام الحضور، والغياب، وغياب الشهر الحالي. اضغط على شهر في **السجل الشهري** لرؤية السجلات اليومية.',
                 'nfe_32_profile_attendance_tab.png', 'تبويبة الحضور'),
                ('تعرض تبويبة **الامتحان الاستثنائي** تفاصيل الامتحان المسجّلة لهذا التسجيل، أو زراً لإضافتها (انظر القسم 6).',
                 'nfe_33_profile_exam_tab.png', 'تبويبة الامتحان الاستثنائي'),
            ]),
            ('h3', 'تعديل الملف'),
            ('steps', [
                ('اضغط **تعديل الملف** (أو **الإجراءات ← تعديل المعلومات** في القائمة). يُفتح النموذج نفسه من 3 خطوات بالقيم المحفوظة. '
                 'غيّر ما يلزم، وانتقل عبر الخطوات، ثم اضغط **إكمال التسجيل** للحفظ.', 'nfe_62_edit_profile.png', 'تعديل تسجيل'),
            ]),
            ('h3', 'رفع صورة الطفل'),
            ('steps', [
                ('اضغط **أيقونة الكاميرا** على صورة الملف، أو **الإجراءات ← رفع صورة** في القائمة. اختر صورة واضحة وحديثة للطفل (JPG أو PNG) واضغط **حفظ**.',
                 'nfe_60_photo_upload.png', 'نموذج رفع الصورة'),
                ('يُعاد فتح الملف بالصورة الجديدة. تُدرج الصورة أيضاً في تصدير Excel وتُطبع على بطاقة الامتحان.', 'nfe_61_photo_saved.png', 'تم حفظ الصورة'),
            ]),
            ('h3', 'بطاقة الامتحان'),
            ('p', 'اضغط **تحميل بطاقة الامتحان (Word)** في رأس الملف لتحميل بطاقة Word قابلة للتعديل تتضمّن صورة الطفل والدورة ورقم التسجيل والشريك '
                  'والاسم الكامل وتاريخ الولادة والجنسية والمحافظة. صحّح الملف أولاً إذا كان هناك خطأ، لأن كل تحميل يقرأ السجل المحفوظ من جديد.'),
        ]},
        # 5 -----------------------------------------------------------------
        {'title': 'الوضع التعليمي والالتحاق بالدورة', 'body': [
            ('p', 'يسجّل **الوضع التعليمي** مستوى الطفل التعليمي عند التسجيل، والبرنامج والدورة والشعبة التي يلتحق بها. وهو مطلوب قبل أن يظهر الطفل في لوائح الحضور.'),
            ('steps', [
                ('افتح الملف، انتقل إلى تبويبة **الوضع التعليمي** واضغط **إضافة** (أو **تعديل** إن وُجد وضع سابق).',
                 'nfe_40_education_form_empty.png', 'نموذج الوضع التعليمي'),
                ('اختر **المستوى التعليمي عند التسجيل**، و**الدورة**، و**البرنامج**، و**الشعبة**، و**تاريخ التسجيل في الدورة**. إذا تسرّب الطفل من مدرسة، أدخل تاريخ التسرّب.',
                 'nfe_41_education_form_filled.png', 'الوضع التعليمي بعد التعبئة'),
                ('اضغط **حفظ البيانات التعليمية**. يُعاد فتح الملف على تبويبة الوضع التعليمي مع الالتحاق الجديد وسطر جديد في **سجل التعليم**.',
                 'nfe_42_education_saved.png', 'الوضع التعليمي المحفوظ'),
            ]),
            ('h3', 'تسجيل الطفل في دورة جديدة'),
            ('steps', [
                ('عند بدء دورة جديدة افتح صفحة **التسجيل في دورة جديدة** للطفل (من زر **اختيار وإعادة التسجيل** في تنبيه التكرار، أو من زر **دورة جديدة** '
                 'في رأس الملف إذا كان دورك يتيحه). يعرض **سجل التسجيل** الدورات التي التحق بها الطفل سابقاً.',
                 'nfe_34_new_round_form.png', 'التسجيل في دورة جديدة'),
                ('املأ الوضع التعليمي للدورة الجديدة واضغط **حفظ البيانات التعليمية**. يُنشأ سجل تسجيل جديد للدورة الحالية وتبقى الدورات السابقة في السجل.', None, None),
            ]),
            ('note', 'تعتمد البرامج المتاحة على عمر الطفل. إذا لم يظهر البرنامج المطلوب في القائمة، تحقّق من تاريخ الولادة.'),
        ]},
        # 6 -----------------------------------------------------------------
        {'title': 'الامتحان الاستثنائي', 'body': [
            ('p', 'يحتاج الأطفال الذين يتقدّمون للامتحان الاستثنائي إلى سجل امتحان على تسجيلهم. لكل تسجيل سجل امتحان واحد.'),
            ('steps', [
                ('افتح الملف، انتقل إلى تبويبة **الامتحان الاستثنائي** واضغط **إضافة امتحان استثنائي**. تؤخذ الإقامة وبلد ومكان الولادة والبرنامج من التسجيل وتظهر باللون الرمادي.',
                 'nfe_50_exam_form_empty.png', 'نموذج الامتحان الاستثنائي'),
                ('تحقّق من **الصف الذي يتقدّم للامتحان له** (يُشتق من مستوى البرنامج)، واختر **لغة امتحان الرياضيات** (عربية، إنكليزية أو فرنسية) و**امتحان اللغة** (إنكليزية أو فرنسية).',
                 'nfe_51_exam_form_filled.png', 'نموذج الامتحان بعد التعبئة'),
                ('اضغط **حفظ**. تظهر رسالة "تم حفظ الامتحان الاستثنائي" وتعرض التبويبة الإجابات المسجّلة. استخدم **تعديل الامتحان الاستثنائي** لتصحيحها لاحقاً.',
                 'nfe_52_exam_saved.png', 'تفاصيل الامتحان المحفوظة'),
            ]),
            ('note', 'إذا كانت الإقامة أو البرنامج الظاهران غير صحيحين، صحّح تسجيل الطفل أولاً (تعديل الملف) ثم عُد إلى نموذج الامتحان.'),
        ]},
        # 7 -----------------------------------------------------------------
        {'title': 'الحضور اليومي', 'body': [
            ('p', 'يُسجَّل الحضور لكل يوم ولكل برنامج وشعبة. افتحه من **الحضور** في القائمة الجانبية.'),
            ('steps', [
                ('التاريخ الافتراضي هو **اليوم**. اختر **البرنامج التعليمي** و**الدورة** و**الشعبة**.', 'nfe_70_attendance_page.png', 'صفحة الحضور'),
                ('اضغط **تحميل**. يظهر الأطفال الملتحقون بهذا البرنامج والشعبة على الجانب، ولكل منهم زرا **حضر** و**غائب**.',
                 'nfe_71_attendance_loaded.png', 'الأطفال المحمَّلون للصف المختار'),
                ('يُعلَّم الأطفال **حضر** افتراضياً. لكل طفل غائب اضغط **غائب** واختر **سبب الغياب** (مرض، نقل، أو غير ذلك – مع وصفه في مربّع النص).',
                 'nfe_72_attendance_marked.png', 'الغياب معلَّم مع سببه'),
                ('اضغط **حفظ**. تؤكّد رسالة **نجاح** حفظ الحضور. يمكنك إعادة تحميل اليوم نفسه لاحقاً لتصحيحه.', 'nfe_73_attendance_saved.png', 'تم حفظ الحضور'),
                ('إذا كان المركز مغلقاً اختر **يوم عطلة** بدلاً من تعليم الأطفال، واختر **سبب الإغلاق** ثم احفظ.', 'nfe_74_attendance_day_off.png', 'تسجيل يوم عطلة'),
            ]),
            ('bullets', [
                'يمكن تسجيل الحضور لليوم أو لتاريخ سابق؛ **التواريخ المستقبلية مرفوضة**.',
                'الطفل الذي لا يظهر في القائمة ليس لديه وضع تعليمي لهذا البرنامج والشعبة (انظر القسم 5)، أو أن تسجيله غير نشط.',
                '**تحميل الملف** يعطي ملف CSV للقائمة المحمَّلة حالياً على الشاشة.',
            ]),
        ]},
        # 8 -----------------------------------------------------------------
        {'title': 'المعلّمون', 'body': [
            ('p', 'يجب تسجيل كل معلّم أو ميسّر في المركز. افتح **المعلّمون** من القائمة الجانبية.'),
            ('steps', [
                ('تعرض قائمة المعلّمين الأسماء والجنس ورقم الهاتف والمركز والدورة ومن أنشأ السجل. استخدم **بحث** للتصفية و**تصدير** لتحميل القائمة. اضغط **إضافة معلّم** لإنشاء سجل.',
                 'nfe_80_teachers_list.png', 'قائمة المعلّمين'),
                ('املأ **الهوية والاتصال**: الأسماء بالأحرف العربية، الجنس، تاريخ الولادة، الجنسية، نوع ورقم الهوية، الهاتف (بالصيغة XX-XXXXXX) والبريد الإلكتروني.',
                 'nfe_81_teacher_form_empty.png', 'نموذج المعلّم'),
                ('املأ **التكليف والمؤهّلات**: المركز، السنة الدراسية، التكليف، ساعات التدريس، المواد، المستويات، مواضيع التدريب، سنوات الخبرة والتدريب الإضافي. '
                 'أضف حتى أربع وثائق داعمة في **الوثائق المطلوبة**.', 'nfe_82_teacher_form_filled.png', 'نموذج المعلّم بعد التعبئة'),
                ('اضغط **إكمال التسجيل**. يظهر المعلّم في القائمة.', 'nfe_83_teacher_saved.png', 'تم حفظ المعلّم'),
                ('لتحديث بيانات معلّم استخدم **الإجراءات ← تعديل** في القائمة، غيّر القيم واحفظ. **حذف** يزيل المعلّم بعد التأكيد.',
                 'nfe_84_teacher_edit.png', 'تعديل معلّم'),
            ]),
        ]},
        # 9 -----------------------------------------------------------------
        {'title': 'المراكز', 'body': [
            ('steps', [
                ('يعرض عنصر **المراكز** في القائمة الجانبية المراكز التي يمكنك الوصول إليها مع الشريك والنوع والموقع. يرى مستخدم المركز مركزه فقط، '
                 'ويرى مستخدم الشريك جميع مراكز منظمته. استخدم إجراءات السطر لفتح أو تحديث ملف المركز (الاسم، النوع، العنوان، الإحداثيات، الخدمات المقدَّمة).',
                 'nfe_85_centers_list.png', 'قائمة المراكز'),
            ]),
        ]},
        # 10 ----------------------------------------------------------------
        {'title': 'تصدير البيانات', 'body': [
            ('p', 'تبدأ عمليات التصدير من قائمة المستفيدين وتُحضَّر في الخلفية، لذا يمكنك متابعة عملك.'),
            ('steps', [
                ('في قائمة المستفيدين اضغط **تصدير**. اختر **الأطفال المراد تصديرهم** (جميع الأطفال الذين يمكنك الوصول إليهم، أو نتائج الفلتر الحالية فقط) '
                 'و**الصيغة**: CSV (نص فقط)، أو Excel مع الصور، أو بطاقات الامتحان Word (ZIP).', 'nfe_13_export_modal.png', 'خيارات التصدير'),
                ('اضغط **بدء التصدير**. عندما يصبح الملف جاهزاً تخبرك رسالة بأن التحميل يبدأ تلقائياً.', 'nfe_14_export_started.png', 'اكتمل التصدير'),
                ('اضغط **أيقونة الجرس** في الشريط العلوي لفتح **عمليات التصدير الأخيرة**. يعرض كل عنصر حالته ويتيح تحميل الملف مجدداً. '
                 '**عرض كل السجل** يفتح سجل التصدير الكامل.', 'nfe_15_export_history.png', 'قائمة عمليات التصدير الأخيرة'),
            ]),
            ('bullets', [
                'يُدرج تصدير Excel صورة كل طفل في السطر نفسه مع رقم الطفل ورقم التسجيل.',
                'ملفات CSV بترميز UTF-8 مع علامة ترتيب البايتات، لذا تُفتح الأسماء العربية بشكل صحيح في Excel.',
                'لا يمكن تحميل ملف التصدير إلا للمستخدم الذي طلبه.',
                '**تحميل بطاقات الامتحان** في القائمة يحضّر بطاقات Word للأطفال المختارين في ملف ZIP واحد.',
            ]),
        ]},
        # 11 ----------------------------------------------------------------
        {'title': 'لوحات المعلومات والتحليلات', 'body': [
            ('p', 'تعطي عناصر **التحليلات** في القائمة الجانبية نظرة عامة على بياناتك. جميع اللوحات محصورة بالمراكز التي يمكنك الوصول إليها.'),
            ('steps', [
                ('**لوحة المعلومات** – إجمالي التسجيلات، المراكز النشطة، الشركاء والدورات، تليها رسوم بيانية عن الجنس والفئات العمرية والجنسية ومصدر التعريف '
                 'والتسجيلات في كل دورة والحالة الأسرية والإعاقة والدعم النقدي والأطفال المنتقلين بين الدورات. استخدم **الفلاتر** لتضييق البيانات.',
                 'nfe_90_dashboard.png', 'لوحة المعلومات التشغيلية'),
                ('**مخرجات التعلّم** – معدّل الحضور، معدّل عمالة الأطفال، الانتقال إلى التعليم النظامي، تحسّن الدرجات والتسرّب، مع رسوم اجتماعية-اقتصادية ورسوم الأثر.',
                 'nfe_91_learning_outcome.png', 'تحليل مخرجات التعلّم'),
                ('**لوحة معلومات المعلّمين** – عدد المعلّمين والجنس والجنسية والتكليفات والمواد والتدريب.', 'nfe_92_teacher_dashboard.png', 'لوحة معلومات المعلّمين'),
                ('**الخريطة الحرارية للحضور** – مربّع لكل يوم ملوّن بحسب معدّل الحضور، إجمالاً ولكل برنامج. الأخضر الداكن حضور مرتفع؛ المربّعات الفاتحة أيام تستحق المتابعة.',
                 'nfe_93_attendance_heatmap.png', 'الخريطة الحرارية للحضور'),
                ('**خريطة المراكز** – المراكز على خريطة مع خصائصها وقائمة الأطفال المسجّلين. صفِّ بحسب الشريك والمركز.', 'nfe_94_centers_map.png', 'خريطة المراكز'),
                ('**منشئ الجداول المحورية** – اسحب الحقول (المركز، القضاء، الجنس، المحافظة، الجنسية، الشريك، البرنامج...) إلى الصفوف والأعمدة لبناء جدولك أو رسمك؛ '
                 'اختر طريقة التجميع (عدد، مجموع...) من القائمة الجانبية.', 'nfe_95_pivot_builder.png', 'منشئ الجداول المحورية'),
            ]),
        ]},
        # 12 ----------------------------------------------------------------
        {'title': 'حسابك', 'body': [
            ('steps', [
                ('**الملف الشخصي** (قائمة المستخدم) يعرض منظمتك الشريكة ومركزك والمعلومات المرتبطة بحسابك. تواصل مع المدير لتغيير هذه الارتباطات.',
                 'nfe_96_profile_page.png', 'صفحة الملف الشخصي'),
                ('**تغيير كلمة المرور** (قائمة المستخدم): أدخل كلمة المرور الحالية ثم الجديدة مرتين، واضغط **تغيير كلمة المرور**.',
                 'nfe_97_change_password.png', 'نموذج تغيير كلمة المرور'),
                ('**تسجيل الخروج** (قائمة المستخدم) ينهي جلستك. سجّل الخروج دائماً عند مغادرة حاسوب مشترك.', 'nfe_98_logout.png', 'تسجيل الخروج'),
            ]),
            ('table', ['قاعدة كلمة المرور', 'المتطلّب'], [
                ['الطول', '8 أحرف على الأقل'],
                ['الأرقام', '3 أرقام على الأقل'],
                ['الأحرف', 'حرف كبير وحرف صغير على الأقل'],
                ['الرموز', 'رمز واحد على الأقل مثل ! @ # $ % & *'],
                ['غير شائعة', 'ليست كلمة شائعة ولا تشبه اسم المستخدم'],
            ]),
        ]},
        # 13 ----------------------------------------------------------------
        {'title': 'الأسئلة الشائعة', 'body': [
            ('table', ['السؤال', 'الجواب'], [
                ['زر الخطوة التالية معطّل في نموذج التسجيل.', 'تم العثور على تكرار محتمل. راجع لوحة المطابقات المحتملة: افتح الملف الموجود أو أعد تسجيل الطفل في دورة جديدة بدلاً من إنشاء سجل جديد.'],
                ['تُمسح الأسماء عند مغادرة الحقل.', 'يجب كتابة الأسماء بالأحرف العربية فقط. تُزال الأحرف اللاتينية والأرقام تلقائياً.'],
                ['رقم الهاتف مرفوض.', 'استخدم الصيغة XX-XXXXXX، مثلاً 03-123456.'],
                ['لا يظهر الطفل في قائمة الحضور.', 'أضف الوضع التعليمي (البرنامج والدورة والشعبة) في ملف الطفل ثم أعد تحميل لائحة الحضور.'],
                ['قائمة القضاء أو القرية فارغة.', 'اختر المحافظة أولاً ثم القضاء. إذا لم تُحمَّل القوائم اضغط "حاول مجدداً" أو حدّث الصفحة.'],
                ['لا أرى أطفال مركز آخر.', 'يرى مستخدم المركز مركزه فقط. اطلب من المنسّق إذا كنت بحاجة إلى نطاق أوسع.'],
                ['نسيت كلمة المرور.', 'لا توجد إعادة تعيين ذاتية. تواصل مع مدير النظام.'],
                ['بمن أتصل للدعم؟', 'بنقطة الاتصال في منظمتك الشريكة أولاً، ثم بفريق دعم BMA عبر المنسّق.'],
            ]),
        ]},
    ],
}

MANUALS = {'en': EN, 'ar': AR}
