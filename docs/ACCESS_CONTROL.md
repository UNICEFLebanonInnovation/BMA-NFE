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
