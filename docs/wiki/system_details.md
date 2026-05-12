# System Overview & Infrastructure

This document automatically generates a snapshot of the technical codebase and infrastructure used in the Student Registration Compiler system.

## Codebase and Structure

### Backend Core Packages (Django & Requirements)
```
wheel==0.45.1
django==5.2.7
django-environ==0.4.3
whitenoise==6.9.0
django-braces==1.17.0
django-crispy-forms==2.4
crispy-bootstrap5==2025.6
crispy-bootstrap3==2024.1
django-model-utils==5.0.0
Pillow==11.3.0
argon2-cffi==21.3.0
django-allauth==65.9.0
psycopg==3.2.9
awesome-slugify==1.6.5
pytz==2025.2
django-redis==4.8.0
redis>=2.10.5
celery==5.5.3
django-celery-beat==2.8.1
django-celery-results==2.6.0
honcho==2.0.0
rcssmin==1.0.6
django-compressor==2.1.1
django-datatables-view==1.13.0
django-mptt==0.16.0
django-makemessages-xgettext==0.1.1
djangorestframework==3.15.2
djangorestframework-jwt-5==1.13.0
markdown==3.8
django-filter==25.1
drf-spectacular==0.27.2
drf-nested-routers==0.11.1
xlsxwriter==0.9.2
tablib==3.7.0
django-import-export==4.3.7
django-jazzmin==3.0.1
django-autocomplete-light==3.9.7
django-admin-rangefilter==0.3.0
django-bootstrap5==25.1
bootstrap3-datetime==2.4
django-tables2==2.7.5
azure-core==1.34.0
azure-storage-blob==12.25.1
openpyxl==2.4.9
django-prettyjson==0.4.1
xlwt==1.3.0
fuzzywuzzy==0.18.0
Levenshtein>=0.27.3
django-storages==1.14.2
six==1.17.0
firebase-admin==6.8.0
grpcio==1.65.5
azure-monitor-opentelemetry==1.8.1
bleach==6.3.0
```

### Frontend Ecosystem
```json
{
  "name": "student_registration",
  "version": "2.0.0",
  "dependencies": {},
  "devDependencies": {

    "browser-sync": "^2.14.0",
    "del": "^2.2.2",
    "gulp": "^3.9.1",
    "gulp-autoprefixer": "^3.1.1",
    "gulp-cssnano": "^2.1.2",
    "gulp-imagemin": "^3.0.3",
    "gulp-pixrem": "^1.0.0",
    "gulp-plumber": "^1.1.0",
    "gulp-rename": "^1.2.2",
    "gulp-sass": "^2.3.2",
    "gulp-uglify": "^2.0.0",
    "gulp-util": "^3.0.7",
    "run-sequence": "^1.2.2"

  },
  "engines": {
    "node": ">=0.8.0"
  }
}

```

### Django Applications & Database Models
The main Django project (`student_registration`) is divided into the following apps, containing the listed database models:

#### `student_registration.locations`
- **`LocationType`**
  - `name (CharField)`
  - `name_en (CharField)`
- **`Location`**
  - `name (CharField)`
  - `name_en (CharField)`
  - `type (ForeignKey)`
  - `latitude (FloatField)`
  - `longitude (FloatField)`
  - `p_code (CharField)`
- **`Center`**
  - `partner (ForeignKey)`
  - `name (CharField)`
  - `governorate (ForeignKey)`
  - `caza (ForeignKey)`
  - `cadaster (ForeignKey)`
  - `longitude (FloatField)`
  - `latitude (FloatField)`
  - `manager_name (CharField)`
  - `phone_number (CharField)`
  - `email (EmailField)`
  - `type (CharField)`
  - `admin_staff_number (IntegerField)`
  - `cwd_accessible (CharField)`
  - `p_code (CharField)`
  - `is_active (BooleanField)`
  - `owner (ForeignKey)`
  - `modified_by (ForeignKey)`
  - `offer_digital_learning (CharField)`
  - `have_digital_hub (CharField)`
  - `neaby_phcc (CharField)`

#### `student_registration.child`
- **`Child`**
  - `first_name (CharField)`
  - `last_name (CharField)`
  - `father_name (CharField)`
  - `mother_fullname (CharField)`
  - `gender (CharField)`
  - `nationality (ForeignKey)`
  - `nationality_other (TextField)`
  - `birthday_year (CharField)`
  - `birthday_month (CharField)`
  - `birthday_day (CharField)`
  - `p_code (CharField)`
  - `address (TextField)`
  - `living_arrangement (CharField)`
  - `disability (ForeignKey)`
  - `marital_status (CharField)`
  - `have_children (CharField)`
  - `children_number (IntegerField)`
  - `have_sibling (CharField)`
  - `siblings_have_disability (CharField)`
  - `mother_pregnant_expecting (CharField)`
  - `fe_unique_id (CharField)`
  - `number (CharField)`
  - `unicef_id (CharField)`
  - `id_type (ForeignKey)`
  - `case_number (CharField)`
  - `case_number_confirm (CharField)`
  - `parent_individual_case_number (CharField)`
  - `parent_individual_case_number_confirm (CharField)`
  - `individual_case_number (CharField)`
  - `individual_case_number_confirm (CharField)`
  - `recorded_number (CharField)`
  - `recorded_number_confirm (CharField)`
  - `parent_national_number (CharField)`
  - `parent_national_number_confirm (CharField)`
  - `national_number (CharField)`
  - `national_number_confirm (CharField)`
  - `parent_extract_record (CharField)`
  - `parent_extract_record_confirm (CharField)`
  - `parent_syrian_national_number (CharField)`
  - `parent_syrian_national_number_confirm (CharField)`
  - `syrian_national_number (CharField)`
  - `syrian_national_number_confirm (CharField)`
  - `parent_sop_national_number (CharField)`
  - `parent_sop_national_number_confirm (CharField)`
  - `sop_national_number (CharField)`
  - `sop_national_number_confirm (CharField)`
  - `parent_other_number (CharField)`
  - `parent_other_number_confirm (CharField)`
  - `other_number (CharField)`
  - `other_number_confirm (CharField)`
  - `father_educational_level (ForeignKey)`
  - `mother_educational_level (ForeignKey)`
  - `first_phone_owner (CharField)`
  - `first_phone_number (CharField)`
  - `first_phone_number_confirm (CharField)`
  - `second_phone_owner (CharField)`
  - `second_phone_number (CharField)`
  - `second_phone_number_confirm (CharField)`
  - `main_caregiver (CharField)`
  - `main_caregiver_other (TextField)`
  - `children_number_under18 (IntegerField)`
  - `caregiver_first_name (CharField)`
  - `caregiver_middle_name (CharField)`
  - `caregiver_last_name (CharField)`
  - `caregiver_mother_name (CharField)`
  - `main_caregiver_nationality (ForeignKey)`
  - `main_caregiver_nationality_other (TextField)`

#### `student_registration.contrib`
- No models defined.

#### `student_registration.dashboard`
- No models defined.

#### `student_registration.students`
- **`Nationality`**
  - `name (CharField)`
  - `code (CharField)`
  - `name_en (CharField)`
- **`IDType`**
  - `name (CharField)`
  - `active (BooleanField)`
- **`Labour`**
  - `name (CharField)`
- **`Person`**
  - `first_name (CharField)`
  - `last_name (CharField)`
  - `father_name (CharField)`
  - `mother_fullname (CharField)`
  - `mother_firstname (CharField)`
  - `mother_lastname (CharField)`
  - `sex (CharField)`
  - `birthday_year (CharField)`
  - `birthday_month (CharField)`
  - `birthday_day (CharField)`
  - `place_of_birth (CharField)`
  - `family_status (CharField)`
  - `have_children (CharField)`
  - `phone (CharField)`
  - `phone_prefix (CharField)`
  - `registered_in_unhcr (CharField)`
  - `id_number (CharField)`
  - `id_type (ForeignKey)`
  - `nationality (ForeignKey)`
  - `mother_nationality (ForeignKey)`
  - `address (TextField)`
  - `p_code (CharField)`
  - `number (CharField)`
  - `unicef_id (CharField)`
- **`Training`**
  - `name (CharField)`
- **`AttachmentType`**
  - `name (CharField)`

#### `student_registration.schools`
- **`PublicHolidays`**
  - `name (CharField)`
  - `start_date (DateField)`
  - `end_date (DateField)`
- **`School`**
  - `number (CharField)`
  - `type (CharField)`
  - `name (CharField)`
  - `director_name (CharField)`
  - `land_phone_number (CharField)`
  - `email (CharField)`
  - `governorate (ForeignKey)`
  - `district (ForeignKey)`
  - `cadaster (ForeignKey)`
  - `longitude (FloatField)`
  - `latitude (FloatField)`
  - `school_capacity (IntegerField)`
  - `empty_building (CharField)`
  - `number_children (IntegerField)`
  - `number_children_male (IntegerField)`
  - `number_children_female (IntegerField)`
  - `number_children_lebanese (IntegerField)`
  - `number_children_non_lebanese (IntegerField)`
  - `number_children_sbp (IntegerField)`
  - `number_children_male_sbp (IntegerField)`
  - `number_children_female_sbp (IntegerField)`
  - `number_children_lebanese_sbp (IntegerField)`
  - `number_children_non_lebanese_sbp (IntegerField)`
  - `CWD_accessible (CharField)`
  - `internet_available (CharField)`
  - `digital_learning_programme (CharField)`
  - `school_digital_capacity (IntegerField)`
  - `weekend (CharField)`
  - `academic_year_start (DateField)`
  - `academic_year_end (DateField)`
  - `academic_year_exam_end (DateField)`
  - `director_phone_number (CharField)`
  - `fax_number (CharField)`
  - `certified_foreign_language (CharField)`
  - `comments (TextField)`
  - `it_name (CharField)`
  - `it_phone_number (CharField)`
  - `attendance_range (IntegerField)`
  - `attendance_from_beginning (BooleanField)`
  - `location (ForeignKey)`
  - `is_bma (BooleanField)`
  - `is_closed (BooleanField)`
  - `owner (ForeignKey)`
  - `modified_by (ForeignKey)`
- **`ClubType`**
  - `name (CharField)`
- **`Club`**
  - `school (ForeignKey)`
  - `club_name (CharField)`
  - `number_clubs (IntegerField)`
  - `club_type (ForeignKey)`
  - `number_children (IntegerField)`
  - `owner (ForeignKey)`
  - `modified_by (ForeignKey)`
- **`Meeting`**
  - `school (ForeignKey)`
  - `meeting_name (CharField)`
  - `meeting_date (DateField)`
  - `number_participants (IntegerField)`
  - `owner (ForeignKey)`
  - `modified_by (ForeignKey)`
- **`CommunityInitiative`**
  - `school (ForeignKey)`
  - `community_group_name (CharField)`
  - `number_initiatives (IntegerField)`
  - `owner (ForeignKey)`
  - `modified_by (ForeignKey)`
- **`HealthVisit`**
  - `school (ForeignKey)`
  - `focal_point_name (CharField)`
  - `number_visits (IntegerField)`
  - `date_first_visit (DateField)`
  - `date_last_visit (DateField)`
  - `summary (TextField)`
  - `owner (ForeignKey)`
  - `modified_by (ForeignKey)`
- **`EducationalLevel`**
  - `name (CharField)`
- **`Section`**
  - `name (CharField)`
- **`CLMRound`**
  - `name (CharField)`
  - `current_year (BooleanField)`
  - `current_round_bridging (BooleanField)`
  - `start_date_bridging (DateField)`
  - `end_date_bridging (DateField)`
  - `start_date_bridging_edit (DateField)`
  - `end_date_bridging_edit (DateField)`
- **`PartnerOrganization`**
  - `name (CharField)`
  - `schools (ManyToManyField)`
  - `short_name (CharField)`
  - `monitoring_evaluation_focal_point_name (CharField)`
  - `monitoring_evaluation_focal_point_phone (CharField)`
  - `monitoring_evaluation_focal_point_email (CharField)`
  - `program_manager_focal_point_name (CharField)`
  - `program_manager_focal_point_phone (CharField)`
  - `program_manager_focal_point_email (CharField)`
  - `active (BooleanField)`

#### `student_registration.clm`
- **`Assessment`**
  - `name (CharField)`
  - `slug (SlugField)`
  - `overview (TextField)`
  - `start_date (DateField)`
  - `end_date (DateField)`
  - `capacity (IntegerField)`
  - `assessment_form (URLField)`
- **`Cycle`**
  - `name (CharField)`
  - `current_cycle (BooleanField)`
- **`Disability`**
  - `name (CharField)`
  - `name_en (CharField)`
  - `active (BooleanField)`
- **`Center`**
  - `name (CharField)`
  - `partner (ForeignKey)`
- **`CLM`**
  - `first_attendance_date (DateField)`
  - `round (ForeignKey)`
  - `governorate (ForeignKey)`
  - `district (ForeignKey)`
  - `cadaster (ForeignKey)`
  - `location (CharField)`
  - `center (ForeignKey)`
  - `language (CharField)`
  - `student (ForeignKey)`
  - `disability (ForeignKey)`
  - `have_labour_single_selection (CharField)`
  - `labour_weekly_income (CharField)`
  - `labours_single_selection (CharField)`
  - `labours_other_specify (CharField)`
  - `labour_hours (IntegerField)`
  - `hh_educational_level (ForeignKey)`
  - `father_educational_level (ForeignKey)`
  - `status (CharField)`
  - `pre_test_score (CharField)`
  - `post_test_score (CharField)`
  - `participation (CharField)`
  - `learning_result (CharField)`
  - `barriers_single (CharField)`
  - `barriers_other (TextField)`
  - `test_done (CharField)`
  - `round_complete (CharField)`
  - `follow_up_type (CharField)`
  - `phone_call_number (IntegerField)`
  - `house_visit_number (IntegerField)`
  - `family_visit_number (IntegerField)`
  - `phone_call_follow_up_result (CharField)`
  - `house_visit_follow_up_result (CharField)`
  - `family_visit_follow_up_result (CharField)`
  - `cp_referral (CharField)`
  - `parent_attended_visits (CharField)`
  - `pss_session_attended (CharField)`
  - `pss_session_number (IntegerField)`
  - `pss_parent_attended (CharField)`
  - `pss_parent_attended_other (TextField)`
  - `covid_session_attended (CharField)`
  - `covid_session_number (IntegerField)`
  - `covid_parent_attended (CharField)`
  - `covid_parent_attended_other (TextField)`
  - `followup_session_attended (CharField)`
  - `followup_session_number (IntegerField)`
  - `followup_parent_attended (CharField)`
  - `followup_parent_attended_other (TextField)`
  - `visits_number (IntegerField)`
  - `child_health_examed (CharField)`
  - `child_health_concern (CharField)`
  - `registration_level (CharField)`
  - `owner (ForeignKey)`
  - `modified_by (ForeignKey)`
  - `deleted (BooleanField)`
  - `dropout_status (BooleanField)`
  - `moved (BooleanField)`
  - `registration_date (DateField)`
  - `partner (ForeignKey)`
  - `internal_number (CharField)`
  - `comments (TextField)`
  - `unsuccessful_pretest_reason (CharField)`
  - `unsuccessful_posttest_reason (CharField)`
  - `phone_number (CharField)`
  - `phone_number_confirm (CharField)`
  - `education_status (CharField)`
  - `id_type (CharField)`
  - `case_number (CharField)`
  - `case_number_confirm (CharField)`
  - `individual_case_number (CharField)`
  - `individual_case_number_confirm (CharField)`
  - `recorded_number (CharField)`
  - `recorded_number_confirm (CharField)`
  - `other_nationality (CharField)`
  - `national_number (CharField)`
  - `national_number_confirm (CharField)`
  - `parent_extract_record (CharField)`
  - `parent_extract_record_confirm (CharField)`
  - `individual_extract_record (CharField)`
  - `individual_extract_record_confirm (CharField)`
  - `syrian_national_number (CharField)`
  - `syrian_national_number_confirm (CharField)`
  - `sop_national_number (CharField)`
  - `sop_national_number_confirm (CharField)`
  - `source_of_identification (CharField)`
  - `source_of_identification_specify (TextField)`
  - `rims_case_number (CharField)`
  - `source_of_transportation (CharField)`
  - `no_child_id_confirmation (CharField)`
  - `no_parent_id_confirmation (CharField)`
  - `parent_id_type (CharField)`
  - `parent_case_number (CharField)`
  - `parent_case_number_confirm (CharField)`
  - `parent_individual_case_number (CharField)`
  - `parent_individual_case_number_confirm (CharField)`
  - `parent_national_number (CharField)`
  - `parent_national_number_confirm (CharField)`
  - `parent_syrian_national_number (CharField)`
  - `parent_syrian_national_number_confirm (CharField)`
  - `parent_sop_national_number (CharField)`
  - `parent_sop_national_number_confirm (CharField)`
  - `parent_other_number (CharField)`
  - `parent_other_number_confirm (CharField)`
  - `other_number (CharField)`
  - `other_number_confirm (CharField)`
  - `referral_programme_type_1 (CharField)`
  - `referral_partner_1 (CharField)`
  - `referral_date_1 (DateField)`
  - `confirmation_date_1 (DateField)`
  - `referral_programme_type_2 (CharField)`
  - `referral_partner_2 (CharField)`
  - `referral_date_2 (DateField)`
  - `confirmation_date_2 (DateField)`
  - `referral_programme_type_3 (CharField)`
  - `referral_partner_3 (CharField)`
  - `referral_date_3 (DateField)`
  - `confirmation_date_3 (DateField)`
  - `followup_call_reason_1 (TextField)`
  - `followup_call_result_1 (TextField)`
  - `followup_call_date_1 (DateField)`
  - `followup_call_reason_2 (TextField)`
  - `followup_call_result_2 (TextField)`
  - `followup_call_date_2 (DateField)`
  - `followup_visit_reason_1 (TextField)`
  - `followup_visit_result_1 (TextField)`
  - `followup_visit_date_1 (DateField)`
  - `caretaker_first_name (CharField)`
  - `caretaker_middle_name (CharField)`
  - `caretaker_last_name (CharField)`
  - `caretaker_mother_name (CharField)`
  - `caretaker_birthday_year (CharField)`
  - `caretaker_birthday_month (CharField)`
  - `caretaker_birthday_day (CharField)`
  - `cycle_completed (BooleanField)`
  - `enrolled_at_school (BooleanField)`
  - `basic_stationery (CharField)`
  - `pss_kit (CharField)`
  - `remote_learning (CharField)`
  - `remote_learning_reasons_not_engaged (CharField)`
  - `reasons_not_engaged_other (TextField)`
  - `reliable_internet (CharField)`
  - `gender_participate (CharField)`
  - `gender_participate_explain (TextField)`
  - `remote_learning_engagement (CharField)`
  - `meet_learning_outcomes (CharField)`
  - `parent_learning_support_rate (CharField)`
  - `covid_message (CharField)`
  - `covid_message_how_often (CharField)`
  - `covid_parents_message (CharField)`
  - `covid_parents_message_how_often (CharField)`
  - `follow_up_done (CharField)`
  - `follow_up_done_with_who (CharField)`
  - `child_received_books (CharField)`
  - `child_received_printout (CharField)`
  - `child_received_internet (CharField)`
  - `referal_wash (CharField)`
  - `referal_health (CharField)`
  - `referal_other (CharField)`
  - `referal_other_specify (TextField)`

#### `student_registration.attendances`
- **`CLMAttendance`**
  - `round_id (IntegerField)`
  - `school (ForeignKey)`
  - `registration_level (CharField)`
  - `attendance_date (DateField)`
  - `day_off (CharField)`
  - `close_reason (CharField)`
- **`CLMAttendanceStudent`**
  - `attendance_day (ForeignKey)`
  - `registration (ForeignKey)`
  - `student (ForeignKey)`
  - `attended (CharField)`
  - `absence_reason (CharField)`
  - `absence_reason_other (CharField)`
- **`CLMStudentAbsences`**
  - `student_id (IntegerField)`
  - `registration_id (IntegerField)`
  - `round_id (IntegerField)`
  - `partner_id (IntegerField)`
  - `school_id (IntegerField)`
  - `student_first_name (CharField)`
  - `student_father_name (CharField)`
  - `student_last_name (CharField)`
  - `school_name (CharField)`
  - `registation_level (CharField)`
  - `absence_starting_date (DateField)`
  - `absence_ending_date (DateField)`
  - `consecutive_absence_days (IntegerField)`
- **`CLMStudentTotalAttendance`**
  - `student_id (IntegerField)`
  - `registration_id (IntegerField)`
  - `round_id (IntegerField)`
  - `partner_id (IntegerField)`
  - `school_id (IntegerField)`
  - `student_first_name (CharField)`
  - `student_father_name (CharField)`
  - `student_last_name (CharField)`
  - `school_name (CharField)`
  - `registation_level (CharField)`
  - `total_attendance_days (IntegerField)`
  - `total_absence_days (IntegerField)`
- **`MSCCAttendance`**
  - `round_id (IntegerField)`
  - `center (ForeignKey)`
  - `education_program (CharField)`
  - `class_section (CharField)`
  - `attendance_date (DateField)`
  - `day_off (CharField)`
  - `close_reason (CharField)`
- **`MSCCAttendanceChild`**
  - `attendance_day (ForeignKey)`
  - `registration (ForeignKey)`
  - `child (ForeignKey)`
  - `attended (CharField)`
  - `absence_reason (CharField)`
  - `absence_reason_other (CharField)`

#### `student_registration.taskapp`
- **`TaskRunLog`**
  - `task_id (CharField)`
  - `task_name (CharField)`
  - `status (CharField)`
  - `started_at (DateTimeField)`
  - `finished_at (DateTimeField)`
  - `result (TextField)`

#### `student_registration.accounts`
- **`LoggedInUser`**
  - `user (OneToOneField)`
  - `session_key (CharField)`

#### `student_registration.users`
- **`User`**
  - `partner (ForeignKey)`
  - `phone_number (CharField)`
  - `school (ForeignKey)`
  - `location (ForeignKey)`
  - `center (ForeignKey)`
  - `locations (ManyToManyField)`
  - `schools (ManyToManyField)`
  - `regions (ManyToManyField)`
- **`Login`**
  - `user (ForeignKey)`
  - `active (BooleanField)`
- **`WebPushToken`**
  - `user (ForeignKey)`
  - `token (CharField)`
  - `created (DateTimeField)`

#### `student_registration.mscc`
- **`Round`**
  - `name (CharField)`
  - `current_year (BooleanField)`
  - `year (PositiveSmallIntegerField)`
- **`RoundPartner`**
  - `round (ForeignKey)`
  - `partner (ForeignKey)`
  - `start_date (DateField)`
  - `end_date (DateField)`
- **`Teacher`**
  - `first_name (CharField)`
  - `father_name (CharField)`
  - `last_name (CharField)`
  - `mother_fullname (CharField)`
  - `sex (CharField)`
  - `birthdate (DateField)`
  - `id_number (CharField)`
  - `id_type (ForeignKey)`
  - `nationality (ForeignKey)`
  - `unicef_id (CharField)`
  - `round (ForeignKey)`
  - `center (ForeignKey)`
  - `email (CharField)`
  - `primary_phone_number (CharField)`
  - `teacher_assignment (CharField)`
  - `teaching_hours_private_school (IntegerField)`
  - `teaching_hours_mscc (IntegerField)`
  - `trainings (ManyToManyField)`
  - `training_sessions_attended (IntegerField)`
  - `training_date_of_completion (DateField)`
  - `extra_coaching (CharField)`
  - `extra_coaching_specify (TextField)`
  - `attach_short_description_1 (CharField)`
  - `attach_file_1 (FileField)`
  - `attach_type_1 (ForeignKey)`
  - `attach_short_description_2 (CharField)`
  - `attach_file_2 (FileField)`
  - `attach_type_2 (ForeignKey)`
  - `attach_short_description_3 (CharField)`
  - `attach_file_3 (FileField)`
  - `attach_type_3 (ForeignKey)`
  - `attach_short_description_4 (CharField)`
  - `attach_file_4 (FileField)`
  - `attach_type_4 (ForeignKey)`
  - `attach_short_description_5 (CharField)`
  - `attach_file_5 (FileField)`
  - `attach_type_5 (ForeignKey)`
  - `owner (ForeignKey)`
  - `modified_by (ForeignKey)`
- **`Registration`**
  - `center (ForeignKey)`
  - `child (ForeignKey)`
  - `student_old (IntegerField)`
  - `partner (ForeignKey)`
  - `round (ForeignKey)`
  - `have_labour (CharField)`
  - `labour_type (CharField)`
  - `labour_type_specify (CharField)`
  - `labour_hours (IntegerField)`
  - `labour_weekly_income (CharField)`
  - `source_of_identification (CharField)`
  - `source_of_identification_specify (TextField)`
  - `type (CharField)`
  - `owner (ForeignKey)`
  - `modified_by (ForeignKey)`
  - `deleted (BooleanField)`
  - `deleted_by (ForeignKey)`
  - `registration_date (DateField)`
  - `partner_unique_number (CharField)`
- **`EducationHistory`**
  - `child (IntegerField)`
  - `student_old (IntegerField)`
  - `registration_id (IntegerField)`
  - `programme_type (CharField)`
  - `programme_id (IntegerField)`
- **`ProvidedServices`**
  - `name (CharField)`
  - `registration (ForeignKey)`
  - `type (CharField)`
  - `category (CharField)`
  - `service_id (IntegerField)`
  - `completed (BooleanField)`
  - `required (BooleanField)`
  - `completion_date (DateField)`
- **`Packages`**
  - `name (CharField)`
  - `type (CharField)`
  - `category (CharField)`
  - `required (BooleanField)`
  - `age (IntegerField)`
  - `min_age (IntegerField)`
  - `max_age (IntegerField)`
- **`InclusionService`**
  - `registration (ForeignKey)`
  - `dropout (CharField)`
  - `parental_engagement (CharField)`
- **`DigitalService`**
  - `registration (ForeignKey)`
  - `using_akelius (CharField)`
  - `akelius_sessions_number (IntegerField)`
  - `akelius_access (CharField)`
  - `akelius_child_equipped (CharField)`
  - `akelius_change_literacy (CharField)`
  - `akelius_change_math (CharField)`
  - `akelius_change_learning (CharField)`
  - `using_lp (CharField)`
  - `lp_sessions_number (IntegerField)`
  - `lp_access (CharField)`
  - `lp_child_equipped (CharField)`
  - `lp_change_literacy (CharField)`
  - `lp_change_math (CharField)`
  - `lp_change_learning (CharField)`
- **`PSSService`**
  - `registration (ForeignKey)`
  - `child_registered (CharField)`
  - `child_living_arrangement (CharField)`
  - `child_vulnerability (CharField)`
  - `child_out_school_reasons (CharField)`
  - `caregivers_distress (CharField)`
  - `caregivers_additional_parenting (CharField)`
  - `child_distress (CharField)`
  - `child_additional_parenting (CharField)`
  - `child_know_seek_help (CharField)`
  - `child_protection_concern (CharField)`
- **`HealthNutritionService`**
  - `registration (ForeignKey)`
  - `baby_breastfed (CharField)`
  - `infant_exclusively_breastfed (CharField)`
  - `eat_solid_food (CharField)`
  - `age_eat_solid_food (CharField)`
  - `immunization_record_screened (CharField)`
  - `vaccine_missing (TextField)`
  - `muac_malnutrition_screening (CharField)`
  - `eating_minimum_meals (CharField)`
  - `child_vaccinated (CharField)`
  - `positive_parenting (CharField)`
  - `development_delays_identified (CharField)`
  - `respond_stressful_events (TextField)`
  - `physical_activity (CharField)`
  - `accessing_reproductive_health (CharField)`
  - `caregiver_counselling (CharField)`
  - `counselling_date (DateField)`
  - `next_counselling_date (DateField)`
  - `caregiver_ecd_counselling (CharField)`
  - `ecd_counselling_date (DateField)`
  - `next_ecd_counselling_date (DateField)`
  - `child_screened_malnutrition (CharField)`
  - `child_malnutrition_screening (CharField)`
  - `child_immunization_screened (CharField)`
  - `missing_vaccine (TextField)`
  - `attended_health_nutrition_session (CharField)`
  - `health_nutrition_session_title (TextField)`
  - `health_nutrition_session_date (DateField)`
- **`HealthNutritionReferral`**
  - `registration (ForeignKey)`
  - `referred_development_delays (CharField)`
  - `development_delays (CharField)`
  - `referred_malnutrition (CharField)`
  - `malnutrition_treatment_center (CharField)`
  - `referred_anc_pnc (CharField)`
  - `phc_center (TextField)`
  - `women_child_referred_iycf (CharField)`
  - `women_child_referred_organization (TextField)`
  - `infant_child_referred_iycf (CharField)`
  - `infant_child_referred_organization (TextField)`
- **`NFEToFEReferralMapping`**
  - `education_component (CharField)`
  - `min_age (IntegerField)`
  - `max_age (IntegerField)`
- **`EducationService`**
  - `registration (ForeignKey)`
  - `education_status (CharField)`
  - `dropout_date (DateField)`
  - `education_program (CharField)`
  - `catch_up_registered (CharField)`
  - `class_section (CharField)`
  - `registration_date (DateField)`
  - `round (ForeignKey)`
- **`EducationRSService`**
  - `registration (ForeignKey)`
  - `school (ForeignKey)`
  - `foreign_language_grade (IntegerField)`
  - `arabic_grade (IntegerField)`
  - `math_grade (IntegerField)`
  - `sciences_grade (IntegerField)`
  - `shift (CharField)`
  - `grade_level (CharField)`
- **`EducationAssessment`**
  - `registration (ForeignKey)`
  - `pre_attended_arabic (CharField)`
  - `pre_modality_arabic (CharField)`
  - `pre_arabic_grade (IntegerField)`
  - `pre_attended_language (CharField)`
  - `pre_modality_language (CharField)`
  - `pre_language_grade (IntegerField)`
  - `pre_attended_math (CharField)`
  - `pre_modality_math (CharField)`
  - `pre_math_grade (IntegerField)`
  - `participation (CharField)`
  - `barriers (CharField)`
  - `barriers_other (TextField)`
  - `post_test_done (CharField)`
  - `school_year_completed (CharField)`
  - `post_attended_arabic (CharField)`
  - `post_modality_arabic (CharField)`
  - `post_arabic_grade (IntegerField)`
  - `post_attended_language (CharField)`
  - `post_modality_language (CharField)`
  - `post_language_grade (IntegerField)`
  - `post_attended_math (CharField)`
  - `post_modality_math (CharField)`
  - `post_math_grade (IntegerField)`
- **`EducationProgrammeAssessment`**
  - `registration (ForeignKey)`
  - `programme_type (CharField)`
- **`YouthKitService`**
  - `registration (ForeignKey)`
  - `volunteering_experience (CharField)`
  - `previous_community_initiative (CharField)`
  - `enrollment_reason (CharField)`
  - `pre_tests_administered (CharField)`
  - `test_diagnostic_done (CharField)`
  - `receive_passing_grade (CharField)`
  - `life_skills_completed (CharField)`
  - `participate_volunteering (CharField)`
  - `volunteering_specify (CharField)`
  - `social_course (CharField)`
  - `yfs_course_completed (CharField)`
  - `training_material (CharField)`
  - `future_path (CharField)`
  - `participate_community_initiatives (CharField)`
  - `community_initiatives_specify (TextField)`
  - `adolescent_attendance (CharField)`
  - `adolescent_dropout_reason (TextField)`
  - `adolescent_dropout_date (DateField)`
  - `youth_trained_mental_health (CharField)`
- **`YouthService`**
  - `registration (ForeignKey)`
  - `service_type (CharField)`
- **`FollowUpService`**
  - `registration (ForeignKey)`
  - `follow_up_type (CharField)`
  - `follow_up_number (IntegerField)`
  - `follow_up_result (CharField)`
  - `dropout_reason (TextField)`
  - `dropout_date (DateField)`
  - `parent_attended_meeting (CharField)`
  - `meeting_type (CharField)`
  - `meeting_number (IntegerField)`
  - `meeting_modality (CharField)`
  - `caregiver_attended (CharField)`
  - `caregiver_attended_other (TextField)`
  - `pfss_sessions (CharField)`
  - `pfss_sessions_number (IntegerField)`
- **`Referral`**
  - `registration (ForeignKey)`
  - `referred_formal_education (CharField)`
  - `referred_school (ForeignKey)`
  - `receive_needed_material (CharField)`
  - `referred_service (CharField)`
  - `referred_service_other (TextField)`
  - `recommended_learning_path (CharField)`
  - `dropout_date (DateField)`
- **`YouthAssessment`**
  - `registration (ForeignKey)`
  - `undertake_post_diagnostic (CharField)`
  - `receive_passing_grade (CharField)`
  - `complete_life_skills (CharField)`
  - `participate_volunteering (CharField)`
  - `volunteering_opportunity (CharField)`
  - `benefit_innovation_course (CharField)`
  - `compelete_yfs_course (CharField)`
  - `training_material (CharField)`
  - `future_path (CharField)`
  - `participate_community_initiatives (CharField)`
  - `attendance (CharField)`
- **`YouthReferral`**
  - `registration (ForeignKey)`
  - `refer_tvet (CharField)`
  - `refer_innovation (CharField)`
- **`Recreational`**
  - `registration (ForeignKey)`
- **`LegoService`**
  - `registration (ForeignKey)`
  - `participating_lego_sessions (CharField)`
  - `participating_education_sessions (CharField)`
  - `participating_lego_play_sessions (CharField)`

#### `student_registration.backends`
- **`ExportHistory`**
  - `export_type (CharField)`
  - `created_by (ForeignKey)`
  - `partner_name (CharField)`
  - `file_format (CharField)`
  - `file_url (URLField)`
  - `status (CharField)`
- **`UserActivity`**
  - `username (CharField)`
  - `path (TextField)`
  - `method (CharField)`
  - `data (TextField)`
  - `timestamp (DateTimeField)`

### Deployment and Docker Configuration
#### Django Dockerfile
```dockerfile
FROM python:3.10-slim-bullseye

ENV DEBIAN_FRONTEND=noninteractive
ENV SSH_PASSWD="root:Docker!"

# Pre-install tools and openssh-server but disable triggers/postinst
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        curl && \
    apt-get install -y --no-install-recommends \
        openssh-server --option=Dpkg::Options::="--force-confdef" \
                       --option=Dpkg::Options::="--force-confold" \
                       --option=Dpkg::Options::="--force-overwrite" || true && \
    echo "$SSH_PASSWD" | chpasswd && \
    mkdir -p /var/run/sshd /root/.ssh && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY ./compose/django/sshd_config /etc/ssh/sshd_config

WORKDIR /code/

ARG REQUIREMENTS_FILE=production.txt
COPY requirements /code/requirements
RUN pip install --no-cache-dir -r /code/requirements/$REQUIREMENTS_FILE

COPY . /code/

RUN python manage.py collectstatic --noinput --settings=config.settings.test

EXPOSE 2222 80

ENTRYPOINT ["/code/compose/django/entrypoint.sh"]
CMD ["/code/compose/django/gunicorn.sh"]

```

#### local.yml (Docker Compose)
```yaml
version: '2'

volumes:
  postgres_data_dev: {}
  postgres_backup_dev: {}

services:
  postgres:
    build: ./compose/postgres
    volumes:
      - postgres_data_dev:/var/lib/postgresql/data
      - postgres_backup_dev:/backups
    environment:
      - POSTGRES_USER=student_registration

  django:
    build:
      context: .
      dockerfile: ./compose/django/Dockerfile
      args:
        - REQUIREMENTS_FILE=local.txt
    command: ./compose/django/start-dev.sh
    depends_on:
      - postgres
    environment:
      - POSTGRES_USER=student_registration
      - DATABASE_URL=postgres://student_registration:postgres@postgres:5432/student_registration
      - USE_DOCKER=yes
    volumes:
      - .:/code
      - .:/home/LogFiles
    ports:
      - "8000:8000"


  pycharm:
    build:
      context: .
      dockerfile: ./compose/django/Dockerfile
      args:
        - REQUIREMENTS_FILE=local.txt
    command: ./compose/django/start-dev.sh
    depends_on:
      - postgres
    environment:
      - POSTGRES_USER=student_registration
      - DATABASE_URL=postgres://student_registration:postgres@postgres:5432/student_registration
    volumes:
      - .:/code
      - .:/home/LogFiles




```

### Environment Configurations
```bash

# PostgreSQL
POSTGRES_PASSWORD=mysecretpass
POSTGRES_USER=postgresuser

# General settings
# DJANGO_READ_DOT_ENV_FILE=True
DJANGO_ADMIN_URL=
DJANGO_SETTINGS_MODULE=
DJANGO_SECRET_KEY=
DJANGO_ALLOWED_HOSTS=

# AWS Settings
DJANGO_AWS_ACCESS_KEY_ID=
DJANGO_AWS_SECRET_ACCESS_KEY=
DJANGO_AWS_STORAGE_BUCKET_NAME=

# Used with email
DJANGO_MAILGUN_API_KEY=
DJANGO_SERVER_EMAIL=
MAILGUN_SENDER_DOMAIN=

# Security! Better to use DNS for this task, but you can use redirect
DJANGO_SECURE_SSL_REDIRECT=False

# django-allauth
DJANGO_ACCOUNT_ALLOW_REGISTRATION=True
# Sentry
DJANGO_SENTRY_DSN=

# Firebase Cloud Messaging server key
FCM_SERVER_KEY=
# Firebase web app configuration
FIREBASE_API_KEY=
FIREBASE_AUTH_DOMAIN=
FIREBASE_PROJECT_ID=
FIREBASE_STORAGE_BUCKET=
FIREBASE_MESSAGING_SENDER_ID=
FIREBASE_APP_ID=
FIREBASE_MEASUREMENT_ID=

DJANGO_OPBEAT_ORGANIZATION_ID
DJANGO_OPBEAT_APP_ID
DJANGO_OPBEAT_SECRET_TOKEN

COMPRESS_ENABLED=


```

### Database Schema Graph
An ER Diagram of the database schema is generated as `schema.png` at the root of the project.
