# Tailwind Migration Report

## What was converted
- Implemented `django-tailwind` integration (dependency + Django settings + dedicated `student_registration.theme` app with Tailwind sources/output and build script).
- Updated base layout to use `{% tailwind_css %}` from `django-tailwind`.
- Ran an automated Bootstrap-to-Tailwind codemod over all `*.html` files (recursive) to replace common Bootstrap utility/component classes with Tailwind utility classes.
- Removed `{% load django_bootstrap5 %}`, `{% bootstrap_css %}`, and `{% bootstrap_javascript %}` template tags from templates.

## Remaining Bootstrap JS dependencies
The following templates still include Bootstrap JS-driven patterns (`data-toggle`, `data-target`, `data-dismiss`, modal/dropdown/collapse/tooltip classes/attributes):

- `student_registration/templates/base.html`
- `student_registration/templates/account/login.html`
- `student_registration/templates/schools/meeting_list.html`
- `student_registration/templates/schools/health_visit_list.html`
- `student_registration/templates/schools/community_initiative_list.html`
- `student_registration/templates/schools/profile.html`
- `student_registration/templates/schools/school_list.html`
- `student_registration/templates/schools/club_list.html`
- `student_registration/templates/clm/list.html`
- `student_registration/templates/clm/bridging_list.html`
- `student_registration/templates/clm/attendance_children.html`
- `student_registration/templates/mscc/list.html`
- `student_registration/templates/mscc/dashboard_youth.html`
- `student_registration/templates/mscc/attendance.html`
- `student_registration/templates/mscc/child_info_tab.html`
- `student_registration/templates/mscc/attendance_children.html`
- `student_registration/templates/mscc/child_profile_preview.html`
- `student_registration/templates/mscc/child_attendance_tab.html`
- `student_registration/templates/mscc/child_services_tab.html`
- `student_registration/templates/mscc/profile.html`
- `student_registration/templates/mscc/teacher_list.html`
- `student_registration/templates/mscc/dashboard_d3.html`
- `student_registration/templates/django_tables2/clm_action_column.html`
- `student_registration/templates/django_tables2/mscc/teacher_action_column.html`
- `student_registration/templates/django_tables2/mscc/action_column.html`
- `student_registration/templates/django_tables2/school/meeting_action_column.html`
- `student_registration/templates/django_tables2/school/initiative_action_column.html`
- `student_registration/templates/django_tables2/school/club_action_column.html`
- `student_registration/templates/django_tables2/students/teacher_action_column.html`
- `student_registration/templates/dashboard/exporter.html`
- `student_registration/templates/location/center_list.html`
- `student_registration/templates/location/center_profile.html`
- `student_registration/templates/location/center_info_tab.html`
- `student_registration/templates/location/program_staff_tab.html`
- `student_registration/templates/students/teacher_list.html`

## Trivial/safe replacements applied now
- Kept Bootstrap JS includes in base template for compatibility during transition.
- Fixed `d-none` → `hidden` mismatch in runtime loader toggling and one attendance conditional block.
- Removed duplicate Bootstrap script include block from base template.

## Recommended next steps (to fully remove Bootstrap)
1. Replace modal/dropdown/collapse interactions with:
   - Alpine.js (`x-data`, `x-show`, `x-transition`) or
   - Headless UI components for Django-rendered markup.
2. Replace tooltip/popover usage (`data-toggle="tooltip"`, custom popovers) with Tippy.js or floating-ui.
3. Replace `django_tables2` bootstrap templates with Tailwind-specific table partials.
4. Move crispy forms from `bootstrap3` pack to a Tailwind-compatible rendering strategy (custom crispy templates or plain Django form rendering).
5. Once JS replacements are complete, remove Bootstrap JS/CDN includes from base and remaining templates.
6. Run `python manage.py tailwind install` (once per environment), then `scripts/build_tailwind.sh` (or `python manage.py tailwind build`) to generate production CSS.
