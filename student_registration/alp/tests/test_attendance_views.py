from types import SimpleNamespace
from unittest.mock import Mock, patch

from django.test import RequestFactory, SimpleTestCase

from student_registration.alp.attendance_views import export_attendance_children


class AttendanceExportTests(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def _request(self, query=None):
        request = self.factory.get('/alp/export-attendance-children/', query or {})
        group_filter = Mock()
        group_filter.exists.return_value = True
        groups = Mock()
        groups.filter.return_value = group_filter
        request.user = SimpleNamespace(
            is_authenticated=True,
            school_id=7,
            groups=groups,
        )
        return request

    def test_export_requires_attendance_filters(self):
        response = export_attendance_children(self._request())

        self.assertEqual(response.status_code, 400)

    @patch('student_registration.alp.attendance_views.load_child_attendance')
    def test_export_downloads_utf8_csv_for_selected_attendance(self, load):
        load.return_value = {
            'instances': [{
                'child_id': 11,
                'child_fullname': 'Test Child',
                'child_mother_fullname': 'Test Mother',
                'child_birthday': '2015-01-02',
                'child_nationality': 'Lebanese',
                'attended': 'Yes',
                'absence_reason': '',
                'absence_reason_other': '',
            }],
            'new_instances': [],
        }
        request = self._request({
            'attendance_date': '2026-09-08',
            'round_id': '3',
            'programme': '2',
        })

        response = export_attendance_children(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv; charset=utf-8')
        self.assertIn('alp-attendance-2026-09-08.csv', response['Content-Disposition'])
        self.assertTrue(response.content.startswith(b'\xef\xbb\xbf'))
        self.assertIn(b'Test Child', response.content)
        load.assert_called_once_with(7, '3', '2026-09-08', '2')
