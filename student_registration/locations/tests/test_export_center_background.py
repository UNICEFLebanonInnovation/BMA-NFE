import unittest
from unittest.mock import patch, MagicMock

from django.http import HttpResponse
from student_registration.locations.views import export_center_background

class TestExportCenterBackground(unittest.TestCase):
    @patch('student_registration.locations.views.connection')
    @patch('student_registration.locations.views.has_group')
    @patch('student_registration.locations.views.ExportStorage')
    @patch('student_registration.locations.views.ExportHistory')
    @patch('student_registration.locations.views.uuid.uuid4')
    @patch('student_registration.locations.views.reverse')
    def test_export_success_unicef(self, mock_reverse, mock_uuid, mock_export_history, mock_export_storage, mock_has_group, mock_connection):
        # Setup mocks
        mock_request = MagicMock()
        mock_request.user.center_id = 1
        mock_request.user.partner_id = None
        mock_request.user.partner = None
        mock_request.GET.get.side_effect = lambda k, d='': ''

        mock_has_group.side_effect = lambda u, g: g == 'MSCC_UNICEF'

        mock_cursor = MagicMock()
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.description = [('id',), ('center_name',), ('type',)]
        mock_cursor.fetchall.return_value = [(1, 'Center A', 'Type X'), (2, 'Center B', 'Type Y')]

        mock_uuid.return_value = '1234-5678'
        mock_reverse.return_value = '/test/url/'

        # We need to mock Teacher locally within the view since it imports it inside the function
        with patch('student_registration.mscc.models.Teacher', create=True) as mock_teacher:
            mock_teacher.objects.filter.return_value.values.return_value.exists.return_value = False

            response = export_center_background(mock_request)

            # Assertions
            self.assertIsInstance(response, HttpResponse)
            self.assertEqual(response.content, b'out_file_1234-5678.zip')

            mock_cursor.execute.assert_called_with("SELECT * FROM vw_center_data WHERE center_id > 0", [])

            mock_export_storage.return_value.save.assert_called_once()

            mock_export_history.objects.create.assert_called_once_with(
                export_type='Center List',
                created_by=mock_request.user,
                file_url='/test/url/',
                status='done',
                partner_name=''
            )

    @patch('student_registration.locations.views.connection')
    @patch('student_registration.locations.views.has_group')
    @patch('student_registration.locations.views.ExportStorage')
    @patch('student_registration.locations.views.ExportHistory')
    @patch('student_registration.locations.views.uuid.uuid4')
    @patch('student_registration.locations.views.reverse')
    def test_export_success_with_teachers(self, mock_reverse, mock_uuid, mock_export_history, mock_export_storage, mock_has_group, mock_connection):
        # Setup mocks
        mock_request = MagicMock()
        mock_request.user.center_id = 1
        mock_request.user.partner_id = 2
        mock_request.user.partner.name = 'Partner A'
        mock_request.GET.get.side_effect = lambda k, d='': ''

        # Test the MSCC_PARTNER flow
        mock_has_group.side_effect = lambda u, g: g == 'MSCC_PARTNER'

        mock_cursor = MagicMock()
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.description = [('id',)]
        mock_cursor.fetchall.return_value = [(1,)]

        mock_uuid.return_value = '1234'
        mock_reverse.return_value = '/test/url/'

        with patch('student_registration.mscc.models.Teacher', create=True) as mock_teacher:
            teacher_mock_qs = MagicMock()
            mock_teacher.objects.filter.return_value.values.return_value = teacher_mock_qs
            teacher_mock_qs.exists.return_value = True
            teacher_mock_qs.__iter__.return_value = [
                {'center__name': 'Center A', 'first_name': 'John', 'last_name': 'Doe', 'sex': 'M', 'email': 'john@test.com', 'primary_phone_number': '123'}
            ]

            response = export_center_background(mock_request)

            self.assertEqual(response.content, b'out_file_1234.zip')
            mock_cursor.execute.assert_called_with("SELECT * FROM vw_center_data WHERE center_id > 0 AND partner_id = %s", [2])

            mock_export_history.objects.create.assert_called_once_with(
                export_type='Center List',
                created_by=mock_request.user,
                file_url='/test/url/',
                status='done',
                partner_name='Partner A'
            )

    @patch('student_registration.locations.views.connection')
    @patch('student_registration.locations.views.has_group')
    @patch('student_registration.locations.views.ExportStorage')
    @patch('student_registration.locations.views.ExportHistory')
    @patch('student_registration.locations.views.uuid.uuid4')
    @patch('student_registration.locations.views.reverse')
    def test_export_filters(self, mock_reverse, mock_uuid, mock_export_history, mock_export_storage, mock_has_group, mock_connection):
        # Setup mocks with filters
        mock_request = MagicMock()
        mock_request.user.center_id = 5
        mock_request.user.partner_id = None

        def get_side_effect(k, d=''):
            if k == 'center_name': return 'Test Name'
            if k == 'center_type': return 'Test Type'
            if k == 'center_governorate': return '10'
            return d
        mock_request.GET.get.side_effect = get_side_effect

        # Test the MSCC_CENTER flow
        mock_has_group.side_effect = lambda u, g: g == 'MSCC_CENTER'

        mock_cursor = MagicMock()
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.description = [('id',)]
        mock_cursor.fetchall.return_value = []

        mock_uuid.return_value = '1234'
        mock_reverse.return_value = '/test/url/'

        response = export_center_background(mock_request)

        self.assertEqual(response.content, b'out_file_1234.zip')

        expected_query = "SELECT * FROM vw_center_data WHERE center_id > 0 AND center_id = %s AND center_name LIKE %s AND center_type LIKE %s AND governorate_id = %s"
        expected_params = [5, '%Test Name%', '%Test Type%', '10']
        mock_cursor.execute.assert_called_with(expected_query, expected_params)

    @patch('student_registration.locations.views.connection')
    def test_export_exception(self, mock_connection):
        # Setup mock to raise exception
        mock_request = MagicMock()
        mock_connection.cursor.side_effect = Exception("DB Connection Failed")

        with patch('student_registration.locations.views.logging') as mock_logging:
            response = export_center_background(mock_request)

            self.assertEqual(response.status_code, 500)
            self.assertEqual(response.content, b'An error occurred: DB Connection Failed')
            mock_logging.error.assert_called()
