from datetime import date
from unittest.mock import MagicMock, patch

from django.test import TestCase

from student_registration.mscc.utils import create_attendance, load_child_attendance


class AttendanceUtilsTests(TestCase):
    @patch("student_registration.mscc.utils.Referral.objects.filter")
    @patch("student_registration.mscc.utils.EducationService.objects.filter")
    @patch("student_registration.mscc.utils.Registration.objects.filter")
    def test_load_child_attendance_filters_by_registration_date(
        self,
        registration_filter_mock,
        _education_service_filter_mock,
        _referral_filter_mock,
    ):
        chain = MagicMock()
        chain.annotate.return_value = chain
        chain.filter.return_value = chain
        chain.exclude.return_value = chain
        chain.__iter__.return_value = iter([])
        registration_filter_mock.return_value = chain

        load_child_attendance(
            center_id=1,
            round_id=2,
            attendance_date_str="2026-04-01",
            education_program="BLN Level 1",
            class_section="A",
        )

        registration_filter_mock.assert_called_once_with(
            center_id=1,
            deleted=False,
            round_id=2,
            registration_date__lte=date(2026, 4, 1),
        )

    @patch("student_registration.mscc.utils.MSCCAttendanceChild.objects.get_or_create")
    @patch("student_registration.mscc.utils.Registration.objects.filter")
    @patch("student_registration.mscc.utils.MSCCAttendance.objects.get_or_create")
    def test_create_attendance_skips_children_before_registration_date(
        self,
        attendance_get_or_create_mock,
        registration_filter_mock,
        attendance_child_get_or_create_mock,
    ):
        attendance = MagicMock()
        attendance_get_or_create_mock.return_value = (attendance, True)

        registration_qs = MagicMock()
        registration_qs.values_list.return_value = [(11, date(2026, 4, 10))]
        registration_filter_mock.return_value = registration_qs

        create_attendance(
            {
                "round_id": 2,
                "education_program": "BLN Level 1",
                "class_section": "A",
                "attendance_date": "2026-04-01",
                "attendance_day_off": False,
                "close_reason": "",
                "children_attendance": [
                    {
                        "child_id": 100,
                        "registration_id": 11,
                        "attended": "Yes",
                        "absence_reason": "",
                        "absence_reason_other": "",
                    }
                ],
            },
            center_id=1,
        )

        attendance_child_get_or_create_mock.assert_not_called()
