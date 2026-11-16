# Access Control List (ACL) Matrix

**Revision: September 2026**

This document outlines the permissions and accessible views for each user role, based on `group_required`
assignments and `has_group` authorization checks within the Django codebase.

## Introduction

The application uses Django's authentication system and custom role checks (via `GroupRequiredMixin` and the
`has_group` helper) to manage user permissions. Each role has specific view access and capabilities across
MSCC (Makani), ALP (Accelerated Learning Programme), CLM (Community Learning), and shared services.

Authorization is applied in three layers:

1. **Group membership** gates whether a view can be opened at all.
2. **Queryset scoping** narrows the data a view returns to the user's assigned `center`, `partner` or
   `school`. This happens even for roles that can open a view across the whole system.
3. **Template filtering** hides actions the user may not perform.

> Keep this file in sync when adding a view or a group. Group names are matched exactly and are
> case-sensitive — note that `CLM_Bridging` and `CLM_Inclusion` use mixed case while the rest are uppercase.

## Roles and Permissions

### `ALP_SCHOOL`
**Capabilities:** School focal points running the Accelerated Learning Programme. Required for **every**
view under `/alp/`; a user without this group receives a 403. All querysets are filtered to the school
linked to the user account by `alp.utils.filter_by_school()`, which returns nothing when no school is set.

Read access (list, detail and reporting views):
- ALPLandingPage
- ChildProfileView
- RegistrationListView
- TeacherListView
- AttendanceView / LoadAttendanceChildren
- TeacherAttendanceView / LoadAttendanceTeachers
- ALPRegistrationDashboardView
- ALPTeacherDashboardView (+ ALPTeacherDashboardDataView)
- ALPAttendanceDashboardView
- ALPSchoolDashboardView (+ ALPSchoolGeoDataView)
- ALPPivotDashboardView (+ ALPPivotDataView) — also open to `is_staff` users for cross-school reporting
- ALPDashboardDataView
- export_attendance_children

Write access (blocked for superusers by `ALPEditPermissionMixin`):
- RegistrationAddView / RegistrationEditView / RegistrationDeleteView
- TeacherAddView / TeacherEditView / TeacherDeleteView
- GradingAddView / GradingEditView
- SchoolProfileView
- save_attendance_children / save_attendance_teachers

**Notable exception:** superusers are deliberately **denied** ALP write access. Site administrators can
review ALP data but cannot enter or alter it.

### `CLM_ATTENDANCE`
**Capabilities:** Focused primarily on tracking and managing CLM attendance.
- AttendanceView

### `CLM_BRIDGING_ALL`
**Capabilities:** Has broad administrative access across CLM bridging components and capabilities to export data and view overarching scopes.
- AttendanceView (via context data adjustments)
- BridgingForm
- BridgingListView
- SchoolListView
- TeacherForm
- TeacherListView
- TeacherViewSet
- bridging_export_data
- bridging_school_export
- export_school_background
- teacher_export_data

### `CLM_Bridging`
**Capabilities:** Primary role for managing the CLM Bridging program, including health visits, meetings, initiatives, clubs, assessments, and follow-ups.
- BridgingAddView
- BridgingEditView
- BridgingFollowupView
- BridgingListView
- BridgingMidAssessmentView
- BridgingPostAssessmentView
- BridgingServiceView
- ClubFormView
- ClubListView
- CommunityInitiativeFormView
- CommunityInitiativeListView
- HealthVisitFormView
- HealthVisitListView
- MeetingFormView
- MeetingListView
- SchoolAddView
- SchoolEditView
- SchoolListView

### `CLM_Inclusion`
**Capabilities:** CLM inclusion workflows. Checked with `has_group` to route users to the inclusion
list and to expose inclusion-specific navigation.
- CLM inclusion list and related inclusion forms

### `CLM_TEACHER`
**Capabilities:** Manages teacher profiles within the CLM module.
- TeacherAddView
- TeacherDeleteView
- TeacherEditView
- TeacherListView

### `EXPORT`
**Capabilities:** Specifically granted access to export functionalities across certain lists.
- SchoolListView (export capabilities)

### `MSCC`
**Capabilities:** Standard MSCC module access, allowing management of MSCC centers, assessments, services, grading, inclusion, and associated youth activities.
- AttendanceView
- CenterFormView
- CenterListView
- DiagnosticAssessmentFormView
- DigitalFormView
- EducationAssessmentFormView
- EducationGradingFormView
- EducationRSServiceFormView
- EducationSchoolGradingFormView
- EducationServiceFormView
- FollowUpFormView
- HealthNutritionFormView
- HealthNutritionReferralFormView
- InclusionFormView
- LegoServiceFormView
- MainAddView
- MainEditView
- MainListView
- NewRoundView
- PSSFormView
- ProfileView
- RecreationalFormView
- ReferralFormView
- TeacherAddView
- TeacherDeleteView
- TeacherEditView
- TeacherListView
- YouthAssessmentFormView
- YouthKitServiceFormView
- YouthReferralFormView
- YouthScoringFormView
- YouthServiceGilFormView
- YouthServiceMaharatiFormView

### `MSCC_CENTER`
**Capabilities:** Similar to the `MSCC` role but limited/filtered to specific centers assigned to the user.
- AttendanceView
- CenterFormView
- CenterListView (filtered)
- DiagnosticAssessmentFormView
- DigitalFormView
- EducationAssessmentFormView
- EducationGradingFormView
- EducationRSServiceFormView
- EducationSchoolGradingFormView
- EducationServiceFormView
- FollowUpFormView
- HealthNutritionFormView
- HealthNutritionReferralFormView
- InclusionFormView
- LegoServiceFormView
- MainAddView
- MainEditView
- MainListView (filtered)
- NewRoundView
- PSSFormView
- RecreationalFormView
- ReferralFormView
- TeacherAddView
- TeacherDeleteView
- TeacherEditView
- TeacherListView
- YouthAssessmentFormView
- YouthKitServiceFormView
- YouthReferralFormView
- YouthScoringFormView
- YouthServiceGilFormView
- YouthServiceMaharatiFormView

### `MSCC_PARTNER`
**Capabilities:** Access for MSCC partner organizations, typically limited to filtering views based on partner assignment. Cannot add or edit most records.
- AttendanceView
- CenterListView (filtered)
- MainListView (filtered)
- TeacherAddView
- TeacherDeleteView
- TeacherEditView
- TeacherListView (filtered)

### `MSCC_MEHE`
**Capabilities:** Broad analytical and view access for MEHE staff. Allows wide visibility over MSCC data and reporting.
- AttendanceReport
- AttendanceView
- CenterListView
- MainListView
- TeacherAddView
- TeacherDeleteView
- TeacherEditView
- TeacherListView

### `YOUTH`
**Capabilities:** Youth-stream users. The group is used to classify accounts in the Django admin (the
user-type filter and the user-type column) and to branch navigation for youth workflows. It carries no
`group_required` view list of its own; youth service forms are reached through the MSCC roles.
- Django admin user-type filtering and display
- Youth-specific navigation branches

## Roles that are configuration only

| Group | Note |
|---|---|
| `MSCC_FULL` | **Retired** (see below). The group is removed by the `users.0002_remove_mscc_full_group` migration. |
| `EXPORT` | Not a `group_required` role. It is checked with `has_group` to reveal export actions on lists that gate them. |
| `YOUTH` | Classification group, as described above. |

## Where this is enforced in code

MSCC Excel exports with photographs and Word examination cards use the same registration scope:
staff, superusers and `MSCC_MEHE` can export all non-deleted registrations; `MSCC_PARTNER` can
export registrations for their assigned partner; `MSCC_CENTER` can export registrations for their
assigned centre. Accounts without one of these roles and a required assignment cannot export child
records. Selecting all registrations ignores search filters, while selecting current filters applies
them within this scope.

`mscc:examination_card` (`/mscc/examination-card/<registration_id>/`) requires authentication and
returns a Word card only for an accessible registration. The profile action follows the same scope.
Background child export status and downloads are limited to the user who created the export.

The **Exceptional Exam** profile section and `mscc:exceptional_exam_form` use scoped MSCC registrations:
staff, superusers and `MSCC_MEHE` can read across registrations; partner users can read their own
partner's registrations; centre users can read their assigned centre's registrations. A plain `MSCC`
user with an assigned centre can read that centre's exam details. Deleted registrations and records
without a child are excluded.

Staff and superusers can add or edit exam details. Assigned centre editors (`MSCC_CENTER`, or plain
`MSCC` users without a partner/UNICEF read role) can add or edit their own centre's registrations.
Partner and UNICEF roles otherwise see the recorded answers without an edit action. The authenticated
form binds its registration from the URL, validates all seven required fields and their residence
hierarchy, and keeps creation/modification audit users. Each registration has one editable exam record.
Governorates and districts reference typed Location records, and a district must belong to its selected
governorate. `mscc:exceptional_exam_location_options` requires an authenticated MSCC account with a
read scope or a staff/superuser account, and returns only the requested parent's districts or villages.

| Mechanism | Location |
|---|---|
| `has_group(user, name)` | `student_registration/users/templatetags/custom_tags.py` |
| `group_required = [...]` | `braces.views.GroupRequiredMixin` on class-based views across the apps |
| ALP group check | `student_registration/alp/utils.py` → `user_has_alp_permission()` |
| ALP school scoping | `student_registration/alp/utils.py` → `filter_by_school()` |
| ALP read-only for superusers | `student_registration/alp/views.py` → `ALPEditPermissionMixin` |
| ALP form dropdown scoping | `student_registration/alp/mixins.py` → `ALPSchoolFilterMixin` |

## Retired role

`MSCC_FULL` is no longer required. It did not bypass the current list filters;
it only added redundant UI checks and selected a fallback table for users with
no data scope. Centre, partner and MEHE list scopes remain unchanged.

- The Add New Child button requires `MSCC_CENTER` plus an assigned centre and partner.
- New Round uses the existing view roles, `MSCC` or `MSCC_CENTER` (or a superuser).
- MEHE and partner groups alone do not enable the New Round action.

Deployment: run `python manage.py migrate`. The `users.0002_remove_mscc_full_group`
data migration removes the old group and its memberships. If a deployment attached
Django model permissions to that group, those grants are preserved as direct
permissions for its existing members only. No replacement role is assigned and no
other group's permissions change. The cleanup is idempotent and intentionally
irreversible: deleted memberships cannot be reconstructed by reversing migrations.

## MEHE role name

The central MSCC role is `MSCC_MEHE`. Deploy the matching code and run
`python manage.py migrate` to apply `users.0003_rename_mscc_unicef_to_mscc_mehe`.
Existing role members and model permissions are preserved. If the destination
group already exists, its memberships and grants are combined with the old
group before removing the old group. Other roles and assignments are unchanged.
