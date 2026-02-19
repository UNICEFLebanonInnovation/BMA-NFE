# Tailwind migration report

## What changed

- Added django-tailwind dependency and theme app scaffolding (manual scaffold because package install/init command was blocked in this environment).
- Kept existing Bootstrap assets in place while adding Tailwind stylesheet include in the main base template.
- Ran an automated class-conversion script recursively across `student_registration/templates/**/*.html`.
- `data-bs-*` attributes were not found; this project mostly uses legacy Bootstrap JS hooks (`data-toggle`, `data-target`).

## Bootstrap JS manual follow-up list

### Collapse (11 files)
- `student_registration/templates/clm/bridging_list.html`
- `student_registration/templates/location/center_list.html`
- `student_registration/templates/mscc/list.html`
- `student_registration/templates/mscc/teacher_list.html`
- `student_registration/templates/schools/club_list.html`
- `student_registration/templates/schools/community_initiative_list.html`
- `student_registration/templates/schools/health_visit_list.html`
- `student_registration/templates/schools/meeting_list.html`
- `student_registration/templates/schools/profile.html`
- `student_registration/templates/schools/school_list.html`
- `student_registration/templates/students/teacher_list.html`

### Dropdown (15 files)
- `student_registration/templates/base.html`
- `student_registration/templates/clm/list.html`
- `student_registration/templates/dashboard/exporter.html`
- `student_registration/templates/django_tables2/clm_action_column.html`
- `student_registration/templates/django_tables2/mscc/action_column.html`
- `student_registration/templates/django_tables2/mscc/teacher_action_column.html`
- `student_registration/templates/django_tables2/school/club_action_column.html`
- `student_registration/templates/django_tables2/school/initiative_action_column.html`
- `student_registration/templates/django_tables2/school/meeting_action_column.html`
- `student_registration/templates/django_tables2/students/teacher_action_column.html`
- `student_registration/templates/location/center_info_tab.html`
- `student_registration/templates/mscc/child_attendance_tab.html`
- `student_registration/templates/mscc/child_info_tab.html`
- `student_registration/templates/mscc/child_profile_preview.html`
- `student_registration/templates/mscc/child_services_tab.html`

### Modal (14 files)
- `student_registration/templates/account/login.html`
- `student_registration/templates/base.html`
- `student_registration/templates/clm/bridging_list.html`
- `student_registration/templates/location/center_list.html`
- `student_registration/templates/location/center_profile.html`
- `student_registration/templates/mscc/list.html`
- `student_registration/templates/mscc/profile.html`
- `student_registration/templates/pages/home.html`
- `student_registration/templates/schools/club_list.html`
- `student_registration/templates/schools/community_initiative_list.html`
- `student_registration/templates/schools/health_visit_list.html`
- `student_registration/templates/schools/meeting_list.html`
- `student_registration/templates/schools/school_list.html`
- `student_registration/templates/students/teacher_list.html`

### Tab (6 files)
- `student_registration/templates/location/center_profile.html`
- `student_registration/templates/mscc/child_attendance_tab.html`
- `student_registration/templates/mscc/child_info_tab.html`
- `student_registration/templates/mscc/child_profile_preview.html`
- `student_registration/templates/mscc/child_services_tab.html`
- `student_registration/templates/mscc/profile.html`

### Popover/Tooltip (7 files)
- `student_registration/templates/base.html`
- `student_registration/templates/location/center_info_tab.html`
- `student_registration/templates/location/program_staff_tab.html`
- `student_registration/templates/mscc/child_info_tab.html`
- `student_registration/templates/mscc/child_profile_preview.html`
- `student_registration/templates/mscc/child_services_tab.html`
- `student_registration/templates/mscc/profile.html`

## Next steps

1. Install `django-tailwind` in CI/runtime and run `python manage.py tailwind init theme` + `python manage.py tailwind build` to replace the placeholder stylesheet.
2. Replace Bootstrap JS interactions (collapse/dropdown/modal/tab/tooltips) with lightweight Alpine.js/HTMX/vanilla alternatives, starting from `student_registration/templates/base.html` and list pages.
3. Remove Bootstrap CSS include once dropdown/collapse/modal flows are verified visually page-by-page.