# -*- coding: utf-8 -*-
# flake8: noqa
"""Content of the ALP module user manual (English and Arabic)."""

EN = {
    'title': 'ALP Module – User Manual',
    'subtitle': 'BMA Platform – Accelerated Learning Programme',
    'audience': 'For school focal points running the Accelerated Learning Programme',
    'intro': [
        'This manual explains, step by step, how to use the **ALP (Accelerated Learning Programme) module** of the BMA '
        'platform. It is written for the school focal points who register ALP students, record daily student and teacher '
        'attendance, enter grades, maintain the school profile and consult the dashboards.',
        'ALP records belong to a **school**. Your account is linked to one school and you only see and edit the data of '
        'that school. If the lists stay empty and a warning is shown, your account is not yet linked to a school: ask your administrator.',
        'Each step is illustrated with a screenshot taken from the system. The data shown is demonstration data only.',
    ],
    'sections': [
        # 1 -----------------------------------------------------------------
        {'title': 'Getting Started – Login and Navigation', 'body': [
            ('p', 'Open Google Chrome or Mozilla Firefox and go to the platform address given to you by your coordinator. '
                  'Accounts are created by the system administrator; there is no self-registration.'),
            ('steps', [
                ('Open the login page and enter your **username** and **password**.', '00_login_empty.png', 'The login page'),
                ('Click **Sign in**. ALP users are taken straight to the **ALP home page**.', '00_login_filled.png', 'Login form with the credentials filled in'),
                ('The home page shows today\'s and this week\'s registrations, the schools reporting, the average attendance of the month, '
                 'a 14-day registration trend and the recent exports. The quick action cards open **New Registration**, **Beneficiary List** '
                 'and **Track Attendance**.', 'alp_01_home.png', 'The ALP home page'),
                ('To change the language click the **globe icon** in the top bar and choose **English** or **العربية**.',
                 'alp_02_language_menu.png', 'Language menu'),
                ('Click your **name** in the top-right corner for **Profile**, **Change Password** and **Logout**.',
                 'alp_03_user_menu.png', 'User menu'),
            ]),
            ('h3', 'The side menu'),
            ('table', ['Menu entry', 'What it opens'], [
                ['Home', 'The ALP home page'],
                ['ALP Registrations', 'The student list, the registration form and the student profiles'],
                ['ALP Attendance', 'Daily student attendance'],
                ['ALP Teacher Attendance', 'Daily teacher attendance'],
                ['School Profile', 'Your school record'],
                ['ALP Teachers', 'The teacher list and the teacher form'],
                ['Registration Dashboard', 'Registration counts and learning outcomes'],
                ['Teacher Dashboard', 'Teacher demographics, assignments and training'],
                ['Attendance Dashboard', 'Attendance heatmap over the year'],
                ['School Dashboard', 'Map of the ALP schools'],
                ['ALP Pivot Builder', 'Build your own cross-tabulations'],
                ['User Guide', 'The documentation inside the system'],
            ]),
            ('note', 'The system logs you out automatically after a period of inactivity. Save your work regularly.'),
        ]},
        # 2 -----------------------------------------------------------------
        {'title': 'The Student List', 'body': [
            ('p', 'Open **ALP Registrations** in the side menu. The list shows every student registered in your school.'),
            ('steps', [
                ('Each row shows the registration ID, names, school, academic year (round), programme and section. Click a column header to sort. '
                 'The three icons in the **Actions** column open the **profile**, **edit** the registration or **delete** it.',
                 'alp_10_list.png', 'The ALP student list'),
                ('Click **Search** to filter by name, academic year, programme, section or date, then **Apply Filters**.',
                 'alp_11_list_search.png', 'The search panel'),
                ('**Export CSV** downloads the current list as a CSV file (UTF-8, Arabic names open correctly in Excel). '
                 '**Add New Child** opens the registration form.', None, None),
            ]),
        ]},
        # 3 -----------------------------------------------------------------
        {'title': 'Registering a Student', 'body': [
            ('p', 'Registration uses a **3-step wizard**: Identity, Caregivers and ALP Enrolment. The student is saved only when you click '
                  '**Complete Registration** on the last step. Fields marked with a red asterisk (*) are mandatory. Names must be written in **Arabic letters**.'),
            ('p', 'While you type the name and date of birth, the **Potential Matches** panel checks for an existing child. If a match is shown, '
                  'review it before continuing instead of creating a duplicate.'),
            ('h3', 'Step 1 – Identity, status and background'),
            ('steps', [
                ('Fill in the **Basic Identity Information**: photo (optional), first, father and family name, date of birth, gender, mother\'s full '
                 'name and nationality.', 'alp_20_reg_step1_empty.png', 'Step 1 – identity'),
                ('Fill in **Status & Background**: P-code and home address (optional), **source of referral** to the NFE sector, unique child number, '
                 'formal education unique ID, **living arrangement**, **disability**, **marital status** and whether the child has children. '
                 'Then click **Next Step**.', 'alp_21_reg_step1_filled.png', 'Step 1 completed'),
            ]),
            ('h3', 'Step 2 – Caregiver details and identification documents'),
            ('steps', [
                ('Answer the household questions (siblings, siblings with disability, mother pregnant), the **parents\' educational level**, the '
                 '**primary phone number** (format XX-XXXXXX) with its confirmation and the person who answers it, the number of children under 18, '
                 'the **primary caregiver** and the caregiver\'s names and nationality.', 'alp_22_reg_step2_empty.png', 'Step 2 – caregiver details'),
                ('Choose the **ID type of the caregiver**. The document fields that apply to that ID type appear: type each number and confirm it '
                 '(for example the UNHCR case number, the individual IDs and the barcode number). Follow the format shown under each field, then click **Next Step**.',
                 'alp_23_reg_step2_filled.png', 'Step 2 completed'),
            ]),
            ('h3', 'Step 3 – ALP enrolment, labour and vulnerability'),
            ('steps', [
                ('Enter the **registration date**, the **academic year (round)**, the **programme** (ALP level) and the **section**. Upload a scanned copy '
                 'or clear photo of the signed **consent form** (PDF or image).', 'alp_24_reg_step3_empty.png', 'Step 3 – ALP enrolment'),
                ('Answer **Does the child participate in work?** (mandatory). If the answer is Yes, the type of work, hours per week, weekly income and '
                 'working conditions appear. Tick the **cash support programmes** the household receives, then click **Complete Registration**.',
                 'alp_25_reg_step3_filled.png', 'Step 3 completed'),
                ('The message "Your data has been sent successfully" confirms the registration and the **student profile** opens.',
                 'alp_26_reg_submitted.png', 'The profile right after registration'),
            ]),
            ('note', 'The school is not shown on the form: it is set automatically from the school linked to your account.'),
        ]},
        # 4 -----------------------------------------------------------------
        {'title': 'The Student Profile', 'body': [
            ('steps', [
                ('The header shows the photo, the full name, the unique ID, the date of birth and age, the school, the programme, the current round and the '
                 'registration number. **Edit Profile** reopens the registration form.', 'alp_30_profile_header.png', 'Profile header and Personal Information tab'),
                ('The **Programme Details** tab shows the ALP registration: school, programme, round, registration date, unique child number, source of referral '
                 'and the child labour answers.', 'alp_31_profile_tab1.png', 'Programme Details tab'),
                ('The **Caregiver & Support** tab shows the caregiver, the phone numbers, the identification documents and the cash support programmes.',
                 'alp_32_profile_tab2.png', 'Caregiver & Support tab'),
                ('To correct a registration click **Edit Profile** (or the pencil icon in the list), update the values through the three steps and click '
                 '**Complete Registration**.', 'alp_33_edit_registration.png', 'Editing a registration'),
                ('To delete a registration click the red bin icon in the list and confirm with **Delete**. This cannot be undone.',
                 'alp_34_delete_confirm.png', 'Delete confirmation'),
            ]),
        ]},
        # 5 -----------------------------------------------------------------
        {'title': 'Student Attendance', 'body': [
            ('p', 'Attendance is recorded per day, programme, round and section. Open **ALP Attendance** in the side menu.'),
            ('steps', [
                ('The date defaults to today. Choose the **Programme**, the **Round** and the **Section**.', 'alp_40_attendance_page.png', 'The attendance page'),
                ('Click **Load**. The students of that class appear with **Attended** and **Absent** buttons.', 'alp_41_attendance_loaded.png', 'Students loaded'),
                ('For each absent student click **Absent** and choose the **absence reason** (Sick, Transportation or Other with a description).',
                 'alp_42_attendance_marked.png', 'Absences marked'),
                ('Click **Save**. A **Success** message confirms the save.', 'alp_43_attendance_saved.png', 'Attendance saved'),
                ('If the school was closed, select **Day Off**, choose the **closing reason** and save instead of marking students.',
                 'alp_44_attendance_day_off.png', 'Recording a day off'),
            ]),
            ('bullets', [
                'Future dates are refused; past dates can be corrected by loading them again.',
                '**Download** gives a CSV of exactly what is loaded on screen. The date, round and programme must be selected first.',
            ]),
        ]},
        # 6 -----------------------------------------------------------------
        {'title': 'Teacher Attendance', 'body': [
            ('steps', [
                ('Open **ALP Teacher Attendance**, pick the **date** and click **Load**.', 'alp_50_teacher_attendance_page.png', 'Teacher attendance page'),
                ('The teachers of your school appear with **Present** and **Absent** buttons.', 'alp_51_teacher_attendance_loaded.png', 'Teachers loaded'),
                ('Mark each teacher, then click **Save**.', 'alp_52_teacher_attendance_marked.png', 'Teacher status marked'),
                ('The confirmation message appears; the whole list is saved in one action.', 'alp_53_teacher_attendance_saved.png', 'Teacher attendance saved'),
            ]),
        ]},
        # 7 -----------------------------------------------------------------
        {'title': 'Teachers', 'body': [
            ('p', 'Open **ALP Teachers** in the side menu to manage the teachers of your school.'),
            ('steps', [
                ('The list shows the teachers of your school with their contact details and round. Click **Add Teacher**.', 'alp_60_teachers_list.png', 'The ALP teacher list'),
                ('Fill in **Identity & Contact** (names in Arabic letters, gender, birth date, nationality, phone in the format XX-XXXXXX, email).',
                 'alp_61_teacher_form_empty.png', 'The teacher form'),
                ('Fill in **Assignment & Qualifications**: academic year, assignment, teaching hours per week under ALP, subjects provided, levels taught, '
                 'training topics, years of experience and extra coaching. Attach up to five supporting documents with their type and description.',
                 'alp_62_teacher_form_filled.png', 'Teacher form completed'),
                ('Click **Complete Registration**. The teacher appears in the list.', 'alp_63_teacher_saved.png', 'Teacher saved'),
                ('Use the row actions to **Edit** or **Delete** a teacher.', 'alp_64_teacher_edit.png', 'Editing a teacher'),
            ]),
        ]},
        # 8 -----------------------------------------------------------------
        {'title': 'Grading', 'body': [
            ('p', 'Grades are entered per student registration. The subjects and the allowed ranges are configured by the administrator.'),
            ('steps', [
                ('Open the grading form from the student list (**Actions**) or the address **ALP → Grading → Add**. Select the **registration** of the student.',
                 'alp_70_grading_form_empty.png', 'The grading form'),
                ('Enter a value for each subject. A value outside the allowed range is rejected.', 'alp_71_grading_form_filled.png', 'Grades entered'),
                ('Click **Save**. The grades are stored with the registration and feed the **Learning Outcomes** section of the Registration Dashboard. '
                 'They can be edited later.', 'alp_72_grading_saved.png', 'Back to the student list after saving'),
            ]),
        ]},
        # 9 -----------------------------------------------------------------
        {'title': 'School Profile', 'body': [
            ('steps', [
                ('Open **School Profile**. Update the **school information** (type, operating shift, programme manager, phone, email), the **location** '
                 '(governorate, district, cadaster and GPS coordinates) and the **provided services** (packages, digital learning, digital hub, number of ALP staff, nearby PHCC).',
                 'alp_80_school_profile.png', 'The school profile form'),
                ('Click **Save changes**. The confirmation appears at the top of the page.', 'alp_81_school_profile_saved.png', 'School profile saved'),
            ]),
            ('note', 'Keep the GPS coordinates accurate: they place your school on the School Dashboard map.'),
        ]},
        # 10 ----------------------------------------------------------------
        {'title': 'Dashboards', 'body': [
            ('p', 'All dashboards are limited to your school.'),
            ('steps', [
                ('**Registration Dashboard** – total registrations, rounds and the **Learning Outcomes** block (children assessed, average achievement, '
                 'progress, achievement by subject), followed by charts on gender, nationality, source of identification and vulnerability.',
                 'alp_90_registration_dashboard.png', 'Registration dashboard'),
                ('**Teacher Dashboard** – number of teachers, gender, nationality, assignments, subjects and training.', 'alp_91_teacher_dashboard.png', 'Teacher dashboard'),
                ('**Attendance Dashboard** – a heatmap with one square per day, overall and per ALP level. Dark green means high attendance.',
                 'alp_92_attendance_dashboard.png', 'Attendance dashboard'),
                ('**School Dashboard** – the ALP schools on a map with their students and teachers. Schools without GPS coordinates are not mapped.',
                 'alp_93_school_dashboard.png', 'School dashboard'),
                ('**ALP Pivot Builder** – drag fields into rows and columns to build your own tables and charts.', 'alp_94_pivot_builder.png', 'Pivot builder'),
            ]),
        ]},
        # 11 ----------------------------------------------------------------
        {'title': 'Your Account', 'body': [
            ('steps', [
                ('**Change Password** (user menu): enter the current password and the new password twice, then click **Change Password**.',
                 'alp_97_change_password.png', 'Change password form'),
                ('**Logout** (user menu) ends the session. Always log out on a shared computer.', None, None),
            ]),
            ('table', ['Password rule', 'Requirement'], [
                ['Length', 'At least 8 characters'],
                ['Digits', 'At least 3 digits'],
                ['Letters', 'At least one upper-case and one lower-case letter'],
                ['Symbol', 'At least one symbol such as ! @ # $ % & *'],
                ['Not common', 'Not a common word and not similar to your username'],
            ]),
        ]},
        # 12 ----------------------------------------------------------------
        {'title': 'Frequently Asked Questions', 'body': [
            ('table', ['Question', 'Answer'], [
                ['The lists are empty and a warning is shown.', 'Your account is not linked to a school. Ask your administrator.'],
                ['The Next Step button is disabled.', 'A potential duplicate was found; check the Potential Matches panel before continuing.'],
                ['My names are erased when I leave the field.', 'Names must be written in Arabic letters only.'],
                ['The phone number or an ID number is refused.', 'Follow the format shown under the field (phone: XX-XXXXXX).'],
                ['A student is missing from the attendance list.', 'Check the programme, round and section of the registration (Programme Details tab).'],
                ['The grading form has no subjects.', 'The grading definitions are configured by the administrator; ask for the missing subject to be added.'],
                ['Can the administrator enter data for me?', 'No. Site administrators can view ALP data but cannot add or edit it; data entry is the school\'s responsibility.'],
                ['I forgot my password.', 'There is no self-service reset. Contact your system administrator.'],
            ]),
        ]},
    ],
}

AR = {
    'title': 'دليل المستخدم – وحدة برنامج التعليم المسرّع (ALP)',
    'subtitle': 'منصة BMA – برنامج التعليم المسرّع',
    'audience': 'لنقاط الاتصال في المدارس التي تنفّذ برنامج التعليم المسرّع',
    'intro': [
        'يشرح هذا الدليل خطوةً بخطوة كيفية استخدام **وحدة برنامج التعليم المسرّع (ALP)** في منصة BMA. وهو موجّه لنقاط الاتصال في المدارس '
        'الذين يسجّلون طلاب البرنامج، ويسجّلون الحضور اليومي للطلاب والمعلّمين، ويدخلون الدرجات، ويحدّثون ملف المدرسة، ويطّلعون على لوحات المعلومات.',
        'سجلات البرنامج تابعة **للمدرسة**. حسابك مرتبط بمدرسة واحدة ولا ترى أو تعدّل إلا بيانات تلك المدرسة. إذا بقيت القوائم فارغة وظهر تنبيه، '
        'فهذا يعني أن حسابك غير مرتبط بمدرسة بعد: اطلب ذلك من المدير.',
        'كل خطوة مرفقة بلقطة شاشة مأخوذة من النظام. البيانات الظاهرة هي بيانات تجريبية فقط.',
    ],
    'sections': [
        # 1 -----------------------------------------------------------------
        {'title': 'البدء – تسجيل الدخول والتنقّل', 'body': [
            ('p', 'افتح متصفّح Google Chrome أو Mozilla Firefox وادخل إلى عنوان المنصة الذي زوّدك به المنسّق. يُنشئ مدير النظام الحسابات؛ لا يوجد تسجيل ذاتي.'),
            ('steps', [
                ('افتح صفحة تسجيل الدخول وأدخل **اسم المستخدم** و**كلمة المرور**.', '00_login_empty.png', 'صفحة تسجيل الدخول'),
                ('اضغط **تسجيل الدخول**. يُنقل مستخدمو البرنامج مباشرة إلى **الصفحة الرئيسية للبرنامج**.', '00_login_filled.png', 'نموذج تسجيل الدخول بعد تعبئته'),
                ('تعرض الصفحة الرئيسية تسجيلات اليوم وهذا الأسبوع، والمدارس التي ترسل بيانات، ومعدّل الحضور الشهري، ومنحنى التسجيلات خلال 14 يوماً، '
                 'وعمليات التصدير الأخيرة. بطاقات الإجراءات السريعة تفتح **تسجيل جديد** و**قائمة المستفيدين** و**متابعة الحضور**.',
                 'alp_01_home.png', 'الصفحة الرئيسية للبرنامج'),
                ('لتغيير اللغة اضغط **أيقونة الكرة الأرضية** في الشريط العلوي واختر **العربية** أو **English**.', 'alp_02_language_menu.png', 'قائمة اللغة'),
                ('اضغط على **اسمك** في أعلى الصفحة للوصول إلى **الملف الشخصي** و**تغيير كلمة المرور** و**تسجيل الخروج**.', 'alp_03_user_menu.png', 'قائمة المستخدم'),
            ]),
            ('h3', 'القائمة الجانبية'),
            ('table', ['عنصر القائمة', 'ما يفتحه'], [
                ['المنزل', 'الصفحة الرئيسية للبرنامج'],
                ['تسجيلات ALP', 'قائمة الطلاب ونموذج التسجيل وملفات الطلاب'],
                ['حضور ALP', 'الحضور اليومي للطلاب'],
                ['حضور معلّمي ALP', 'الحضور اليومي للمعلّمين'],
                ['ملف المدرسة', 'سجل مدرستك'],
                ['معلّمو ALP', 'قائمة المعلّمين ونموذج المعلّم'],
                ['لوحة معلومات التسجيل', 'أعداد التسجيلات ومخرجات التعلّم'],
                ['لوحة معلومات المعلّمين', 'بيانات المعلّمين وتكليفاتهم وتدريبهم'],
                ['لوحة معلومات الحضور', 'الخريطة الحرارية للحضور على مدار السنة'],
                ['لوحة معلومات المدارس', 'خريطة مدارس البرنامج'],
                ['منشئ الجداول المحورية', 'بناء جداولك المتقاطعة الخاصة'],
                ['دليل المستخدم', 'التوثيق داخل النظام'],
            ]),
            ('note', 'يُخرجك النظام تلقائياً بعد فترة من عدم النشاط. احفظ عملك بانتظام.'),
        ]},
        # 2 -----------------------------------------------------------------
        {'title': 'قائمة الطلاب', 'body': [
            ('p', 'افتح **تسجيلات ALP** من القائمة الجانبية. تعرض القائمة كل طالب مسجّل في مدرستك.'),
            ('steps', [
                ('يعرض كل سطر رقم التسجيل والأسماء والمدرسة والسنة الدراسية (الدورة) والبرنامج والشعبة. اضغط على عنوان العمود للفرز. '
                 'الأيقونات الثلاث في عمود **الإجراءات** تفتح **الملف**، أو **تعدّل** التسجيل، أو **تحذفه**.', 'alp_10_list.png', 'قائمة طلاب البرنامج'),
                ('اضغط **بحث** للتصفية بحسب الاسم أو السنة الدراسية أو البرنامج أو الشعبة أو التاريخ، ثم **تطبيق الفلاتر**.', 'alp_11_list_search.png', 'لوحة البحث'),
                ('**تصدير CSV** يحمّل القائمة الحالية كملف CSV (بترميز UTF-8، تُفتح الأسماء العربية بشكل صحيح في Excel). **إضافة طفل جديد** يفتح نموذج التسجيل.', None, None),
            ]),
        ]},
        # 3 -----------------------------------------------------------------
        {'title': 'تسجيل طالب', 'body': [
            ('p', 'يستخدم التسجيل **معالجاً من 3 خطوات**: الهوية، مقدّمو الرعاية، الالتحاق بالبرنامج. لا يُحفظ الطالب إلا عند الضغط على **إكمال التسجيل** '
                  'في الخطوة الأخيرة. الحقول المعلَّمة بنجمة حمراء (*) إلزامية. يجب كتابة الأسماء **بالأحرف العربية**.'),
            ('p', 'أثناء كتابة الاسم وتاريخ الولادة تتحقّق لوحة **مطابقات محتملة** من وجود طفل مسجّل سابقاً. إذا ظهرت مطابقة راجعها قبل المتابعة بدلاً من إنشاء سجل مكرّر.'),
            ('h3', 'الخطوة 1 – الهوية والوضع والخلفية'),
            ('steps', [
                ('املأ **معلومات الهوية الأساسية**: الصورة (اختيارية)، الاسم الأول واسم الأب واسم العائلة، تاريخ الولادة، الجنس، اسم الأم الكامل والجنسية.',
                 'alp_20_reg_step1_empty.png', 'الخطوة 1 – الهوية'),
                ('املأ **الوضع والخلفية**: الرمز الجغرافي وعنوان المنزل (اختياريان)، **مصدر الإحالة** إلى قطاع التعليم غير النظامي، رقم الطفل الفريد، الرقم الفريد في التعليم النظامي، '
                 '**ترتيب السكن**، **الإعاقة**، **الحالة الزوجية** وما إذا كان لدى الطفل أطفال. ثم اضغط **الخطوة التالية**.', 'alp_21_reg_step1_filled.png', 'الخطوة 1 بعد التعبئة'),
            ]),
            ('h3', 'الخطوة 2 – بيانات مقدّم الرعاية ووثائق الهوية'),
            ('steps', [
                ('أجب عن أسئلة الأسرة (الإخوة، إخوة من ذوي الإعاقة، حمل الأم)، و**المستوى التعليمي للوالدين**، و**رقم الهاتف الأساسي** (بالصيغة XX-XXXXXX) مع تأكيده '
                 'ومن يجيب عليه، وعدد الأطفال دون 18 سنة، و**مقدّم الرعاية الأساسي** وأسماءه وجنسيته.', 'alp_22_reg_step2_empty.png', 'الخطوة 2 – بيانات مقدّم الرعاية'),
                ('اختر **نوع هوية مقدّم الرعاية**. تظهر حقول الوثائق الخاصة بهذا النوع: اكتب كل رقم وأكّده (مثلاً رقم ملف المفوضية، الأرقام الفردية ورقم الباركود). '
                 'اتّبع الصيغة الظاهرة تحت كل حقل ثم اضغط **الخطوة التالية**.', 'alp_23_reg_step2_filled.png', 'الخطوة 2 بعد التعبئة'),
            ]),
            ('h3', 'الخطوة 3 – الالتحاق بالبرنامج والعمل والهشاشة'),
            ('steps', [
                ('أدخل **تاريخ التسجيل** و**السنة الدراسية (الدورة)** و**البرنامج** (مستوى ALP) و**الشعبة**. ارفع نسخة ممسوحة أو صورة واضحة لنموذج **الموافقة** الموقّع (PDF أو صورة).',
                 'alp_24_reg_step3_empty.png', 'الخطوة 3 – الالتحاق بالبرنامج'),
                ('أجب عن سؤال **هل يشارك الطفل في عمل؟** (إلزامي). إذا كانت الإجابة نعم تظهر حقول نوع العمل وساعات الأسبوع والدخل الأسبوعي وظروف العمل. '
                 'علّم **برامج الدعم النقدي** التي تتلقّاها الأسرة ثم اضغط **إكمال التسجيل**.', 'alp_25_reg_step3_filled.png', 'الخطوة 3 بعد التعبئة'),
                ('تؤكّد رسالة "تم إرسال البيانات بنجاح" التسجيل ويُفتح **ملف الطالب**.', 'alp_26_reg_submitted.png', 'الملف مباشرة بعد التسجيل'),
            ]),
            ('note', 'لا تظهر المدرسة في النموذج: تُحدَّد تلقائياً من المدرسة المرتبطة بحسابك.'),
        ]},
        # 4 -----------------------------------------------------------------
        {'title': 'ملف الطالب', 'body': [
            ('steps', [
                ('يعرض رأس الصفحة الصورة والاسم الكامل والرقم الفريد وتاريخ الولادة والعمر والمدرسة والبرنامج والدورة الحالية ورقم التسجيل. **تعديل الملف** يعيد فتح نموذج التسجيل.',
                 'alp_30_profile_header.png', 'رأس الملف وتبويبة المعلومات الشخصية'),
                ('تعرض تبويبة **تفاصيل البرنامج** تسجيل ALP: المدرسة، البرنامج، الدورة، تاريخ التسجيل، رقم الطفل الفريد، مصدر الإحالة وإجابات عمالة الأطفال.',
                 'alp_31_profile_tab1.png', 'تبويبة تفاصيل البرنامج'),
                ('تعرض تبويبة **مقدّم الرعاية والدعم** مقدّم الرعاية وأرقام الهاتف ووثائق الهوية وبرامج الدعم النقدي.', 'alp_32_profile_tab2.png', 'تبويبة مقدّم الرعاية والدعم'),
                ('لتصحيح تسجيل اضغط **تعديل الملف** (أو أيقونة القلم في القائمة)، حدّث القيم عبر الخطوات الثلاث واضغط **إكمال التسجيل**.',
                 'alp_33_edit_registration.png', 'تعديل تسجيل'),
                ('لحذف تسجيل اضغط أيقونة سلة المهملات الحمراء في القائمة وأكّد بالضغط على **حذف**. لا يمكن التراجع عن الحذف.', 'alp_34_delete_confirm.png', 'تأكيد الحذف'),
            ]),
        ]},
        # 5 -----------------------------------------------------------------
        {'title': 'حضور الطلاب', 'body': [
            ('p', 'يُسجَّل الحضور لكل يوم وبرنامج ودورة وشعبة. افتح **حضور ALP** من القائمة الجانبية.'),
            ('steps', [
                ('التاريخ الافتراضي هو اليوم. اختر **البرنامج** و**الدورة** و**الشعبة**.', 'alp_40_attendance_page.png', 'صفحة الحضور'),
                ('اضغط **تحميل**. يظهر طلاب هذا الصف مع زرّي **حضر** و**غائب**.', 'alp_41_attendance_loaded.png', 'الطلاب المحمَّلون'),
                ('لكل طالب غائب اضغط **غائب** واختر **سبب الغياب** (مرض، نقل، أو غير ذلك مع وصف).', 'alp_42_attendance_marked.png', 'الغياب معلَّم'),
                ('اضغط **حفظ**. تؤكّد رسالة **نجاح** الحفظ.', 'alp_43_attendance_saved.png', 'تم حفظ الحضور'),
                ('إذا كانت المدرسة مغلقة اختر **يوم عطلة** وحدّد **سبب الإغلاق** واحفظ بدلاً من تعليم الطلاب.', 'alp_44_attendance_day_off.png', 'تسجيل يوم عطلة'),
            ]),
            ('bullets', [
                'التواريخ المستقبلية مرفوضة؛ يمكن تصحيح التواريخ السابقة بإعادة تحميلها.',
                '**تحميل الملف** يعطي ملف CSV لما هو محمَّل على الشاشة بالضبط. يجب اختيار التاريخ والدورة والبرنامج أولاً.',
            ]),
        ]},
        # 6 -----------------------------------------------------------------
        {'title': 'حضور المعلّمين', 'body': [
            ('steps', [
                ('افتح **حضور معلّمي ALP**، اختر **التاريخ** واضغط **تحميل**.', 'alp_50_teacher_attendance_page.png', 'صفحة حضور المعلّمين'),
                ('يظهر معلّمو مدرستك مع زرّي **حاضر** و**غائب**.', 'alp_51_teacher_attendance_loaded.png', 'المعلّمون المحمَّلون'),
                ('علّم حالة كل معلّم ثم اضغط **حفظ**.', 'alp_52_teacher_attendance_marked.png', 'حالة المعلّمين معلَّمة'),
                ('تظهر رسالة التأكيد؛ تُحفظ القائمة كاملة في إجراء واحد.', 'alp_53_teacher_attendance_saved.png', 'تم حفظ حضور المعلّمين'),
            ]),
        ]},
        # 7 -----------------------------------------------------------------
        {'title': 'المعلّمون', 'body': [
            ('p', 'افتح **معلّمو ALP** من القائمة الجانبية لإدارة معلّمي مدرستك.'),
            ('steps', [
                ('تعرض القائمة معلّمي مدرستك مع بيانات الاتصال والدورة. اضغط **إضافة معلّم**.', 'alp_60_teachers_list.png', 'قائمة معلّمي البرنامج'),
                ('املأ **الهوية والاتصال** (الأسماء بالأحرف العربية، الجنس، تاريخ الولادة، الجنسية، الهاتف بالصيغة XX-XXXXXX، البريد الإلكتروني).',
                 'alp_61_teacher_form_empty.png', 'نموذج المعلّم'),
                ('املأ **التكليف والمؤهّلات**: السنة الدراسية، التكليف، ساعات التدريس الأسبوعية في البرنامج، المواد، المستويات، مواضيع التدريب، سنوات الخبرة والتدريب الإضافي. '
                 'أرفق حتى خمس وثائق داعمة مع نوعها ووصفها.', 'alp_62_teacher_form_filled.png', 'نموذج المعلّم بعد التعبئة'),
                ('اضغط **إكمال التسجيل**. يظهر المعلّم في القائمة.', 'alp_63_teacher_saved.png', 'تم حفظ المعلّم'),
                ('استخدم إجراءات السطر **لتعديل** أو **حذف** معلّم.', 'alp_64_teacher_edit.png', 'تعديل معلّم'),
            ]),
        ]},
        # 8 -----------------------------------------------------------------
        {'title': 'الدرجات', 'body': [
            ('p', 'تُدخل الدرجات لكل تسجيل طالب. يحدّد المدير المواد والنطاقات المسموح بها.'),
            ('steps', [
                ('افتح نموذج الدرجات من قائمة الطلاب (**الإجراءات**) أو من العنوان **ALP ← الدرجات ← إضافة**. اختر **تسجيل** الطالب.',
                 'alp_70_grading_form_empty.png', 'نموذج الدرجات'),
                ('أدخل قيمة لكل مادة. تُرفض أي قيمة خارج النطاق المسموح.', 'alp_71_grading_form_filled.png', 'الدرجات بعد الإدخال'),
                ('اضغط **حفظ**. تُخزَّن الدرجات مع التسجيل وتغذّي قسم **مخرجات التعلّم** في لوحة معلومات التسجيل. يمكن تعديلها لاحقاً.',
                 'alp_72_grading_saved.png', 'العودة إلى قائمة الطلاب بعد الحفظ'),
            ]),
        ]},
        # 9 -----------------------------------------------------------------
        {'title': 'ملف المدرسة', 'body': [
            ('steps', [
                ('افتح **ملف المدرسة**. حدّث **معلومات المدرسة** (النوع، الدوام، مدير البرنامج، الهاتف، البريد الإلكتروني)، و**الموقع** (المحافظة، القضاء، المنطقة العقارية، '
                 'الإحداثيات)، و**الخدمات المقدَّمة** (الحزم، التعلّم الرقمي، المركز الرقمي، عدد موظفي البرنامج، مركز الرعاية الصحية الأولية القريب).',
                 'alp_80_school_profile.png', 'نموذج ملف المدرسة'),
                ('اضغط **حفظ التغييرات**. يظهر التأكيد في أعلى الصفحة.', 'alp_81_school_profile_saved.png', 'تم حفظ ملف المدرسة'),
            ]),
            ('note', 'حافظ على دقّة الإحداثيات: فهي تحدّد موقع مدرستك على خريطة لوحة معلومات المدارس.'),
        ]},
        # 10 ----------------------------------------------------------------
        {'title': 'لوحات المعلومات', 'body': [
            ('p', 'جميع لوحات المعلومات محصورة بمدرستك.'),
            ('steps', [
                ('**لوحة معلومات التسجيل** – إجمالي التسجيلات والدورات وكتلة **مخرجات التعلّم** (الأطفال المقيَّمون، متوسط التحصيل، التقدّم، التحصيل بحسب المادة)، '
                 'تليها رسوم بيانية عن الجنس والجنسية ومصدر التعريف والهشاشة.', 'alp_90_registration_dashboard.png', 'لوحة معلومات التسجيل'),
                ('**لوحة معلومات المعلّمين** – عدد المعلّمين والجنس والجنسية والتكليفات والمواد والتدريب.', 'alp_91_teacher_dashboard.png', 'لوحة معلومات المعلّمين'),
                ('**لوحة معلومات الحضور** – خريطة حرارية بمربّع لكل يوم، إجمالاً ولكل مستوى من مستويات البرنامج. الأخضر الداكن يعني حضوراً مرتفعاً.',
                 'alp_92_attendance_dashboard.png', 'لوحة معلومات الحضور'),
                ('**لوحة معلومات المدارس** – مدارس البرنامج على خريطة مع طلابها ومعلّميها. المدارس من دون إحداثيات لا تظهر على الخريطة.',
                 'alp_93_school_dashboard.png', 'لوحة معلومات المدارس'),
                ('**منشئ الجداول المحورية** – اسحب الحقول إلى الصفوف والأعمدة لبناء جداولك ورسومك الخاصة.', 'alp_94_pivot_builder.png', 'منشئ الجداول المحورية'),
            ]),
        ]},
        # 11 ----------------------------------------------------------------
        {'title': 'حسابك', 'body': [
            ('steps', [
                ('**تغيير كلمة المرور** (قائمة المستخدم): أدخل كلمة المرور الحالية ثم الجديدة مرتين، واضغط **تغيير كلمة المرور**.', 'alp_97_change_password.png', 'نموذج تغيير كلمة المرور'),
                ('**تسجيل الخروج** (قائمة المستخدم) ينهي الجلسة. سجّل الخروج دائماً على الحاسوب المشترك.', None, None),
            ]),
            ('table', ['قاعدة كلمة المرور', 'المتطلّب'], [
                ['الطول', '8 أحرف على الأقل'],
                ['الأرقام', '3 أرقام على الأقل'],
                ['الأحرف', 'حرف كبير وحرف صغير على الأقل'],
                ['الرموز', 'رمز واحد على الأقل مثل ! @ # $ % & *'],
                ['غير شائعة', 'ليست كلمة شائعة ولا تشبه اسم المستخدم'],
            ]),
        ]},
        # 12 ----------------------------------------------------------------
        {'title': 'الأسئلة الشائعة', 'body': [
            ('table', ['السؤال', 'الجواب'], [
                ['القوائم فارغة ويظهر تنبيه.', 'حسابك غير مرتبط بمدرسة. اطلب ذلك من المدير.'],
                ['زر الخطوة التالية معطّل.', 'تم العثور على تكرار محتمل؛ راجع لوحة المطابقات المحتملة قبل المتابعة.'],
                ['تُمسح الأسماء عند مغادرة الحقل.', 'يجب كتابة الأسماء بالأحرف العربية فقط.'],
                ['رقم الهاتف أو رقم الهوية مرفوض.', 'اتّبع الصيغة الظاهرة تحت الحقل (الهاتف: XX-XXXXXX).'],
                ['طالب غير موجود في قائمة الحضور.', 'تحقّق من البرنامج والدورة والشعبة في التسجيل (تبويبة تفاصيل البرنامج).'],
                ['نموذج الدرجات لا يحتوي على مواد.', 'يحدّد المدير تعريفات الدرجات؛ اطلب إضافة المادة الناقصة.'],
                ['هل يستطيع المدير إدخال البيانات بدلاً مني؟', 'لا. يمكن لمديري النظام الاطّلاع على بيانات البرنامج لكن لا يمكنهم إضافتها أو تعديلها؛ إدخال البيانات مسؤولية المدرسة.'],
                ['نسيت كلمة المرور.', 'لا توجد إعادة تعيين ذاتية. تواصل مع مدير النظام.'],
            ]),
        ]},
    ],
}

MANUALS = {'en': EN, 'ar': AR}
