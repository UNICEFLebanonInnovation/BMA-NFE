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

### `MSCC_FULL`
**Capabilities:** High-level access with unrestricted viewing privileges, primarily bypassing filters in lists.
- MainListView (unrestricted access)

### `MSCC_PARTNER`
**Capabilities:** Access for MSCC partner organizations, typically limited to filtering views based on partner assignment. Cannot add or edit most records.
- AttendanceView
- CenterListView (filtered)
- MainListView (filtered)
- TeacherAddView
- TeacherDeleteView
- TeacherEditView
- TeacherListView (filtered)

### `MSCC_UNICEF`
**Capabilities:** Broad analytical and view access for UNICEF staff. Allows wide visibility over MSCC data and reporting.
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
| `MSCC_FULL` | Not a `group_required` role. It is checked with `has_group` to bypass the center/partner filter on `MainListView`. |
| `EXPORT` | Not a `group_required` role. It is checked with `has_group` to reveal export actions on lists that gate them. |
| `YOUTH` | Classification group, as described above. |

## Where this is enforced in code

| Mechanism | Location |
|---|---|
| `has_group(user, name)` | `student_registration/users/templatetags/custom_tags.py` |
| `group_required = [...]` | `braces.views.GroupRequiredMixin` on class-based views across the apps |
| ALP group check | `student_registration/alp/utils.py` → `user_has_alp_permission()` |
| ALP school scoping | `student_registration/alp/utils.py` → `filter_by_school()` |
| ALP read-only for superusers | `student_registration/alp/views.py` → `ALPEditPermissionMixin` |
| ALP form dropdown scoping | `student_registration/alp/mixins.py` → `ALPSchoolFilterMixin` |
