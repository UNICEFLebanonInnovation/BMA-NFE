# Access Control List (ACL) Matrix

This document outlines the permissions and accessible views for each user role in the student registration system based on `group_required` assignments and `has_group` authorization checks within the Django codebase.

## Introduction

The application uses Django's authentication system and custom role checks (via `GroupRequiredMixin` and `has_group` functions) to manage user permissions. Each role has specific view access and capabilities, particularly for models related to MSCC (Makani), CLM (Community Learning Centers), and other system services. Some views restrict their data inherently based on the role, such as filtering a queryset by a user's assigned partner or center.

## Roles and Permissions

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

## Retired role

`MSCC_FULL` is no longer required. It did not bypass the current list filters;
it only added redundant UI checks and selected a fallback table for users with
no data scope. Centre, partner and UNICEF list scopes remain unchanged.

- The Add New Child button requires `MSCC_CENTER` plus an assigned centre and partner.
- New Round uses the existing view roles, `MSCC` or `MSCC_CENTER` (or a superuser).
- UNICEF and partner groups alone do not enable the New Round action.

Deployment: run `python manage.py migrate`. The `users.0002_remove_mscc_full_group`
data migration removes the old group and its memberships. If a deployment attached
Django model permissions to that group, those grants are preserved as direct
permissions for its existing members only. No replacement role is assigned and no
other group's permissions change. The cleanup is idempotent and intentionally
irreversible: deleted memberships cannot be reconstructed by reversing migrations.
