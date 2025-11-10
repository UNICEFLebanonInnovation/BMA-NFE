import datetime
import json
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pathlib
import sys
import os

import django

import pytest
from rest_framework.test import APIRequestFactory

PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

os.environ.setdefault('DATABASE_URL', 'sqlite:///test.sqlite3')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.test')
django.setup()

from student_registration.mscc.attendance_views import AttendanceHeatmapViewSet


def test_attendance_heatmap_api_monthly_percentages():
    request = APIRequestFactory().get('/attendance-heatmap-data/percentage/', {'year': '2024'})
    request.user = SimpleNamespace(is_authenticated=True)

    base_qs = MagicMock(name='base_qs')

    with patch(
        'student_registration.mscc.attendance_views.MSCCAttendanceChild.objects.filter',
        return_value=base_qs,
    ) as mock_filter, patch(
        'student_registration.mscc.attendance_views.MSCCAttendanceChild.objects.dates',
        return_value=[datetime.date(2023, 1, 1), datetime.date(2024, 1, 1)],
    ) as mock_dates:

        def aggregate_side_effect(qs, *groups):
            assert qs is base_qs
            if groups == ('attendance_day__attendance_date__month',):
                return [
                    {'attendance_day__attendance_date__month': 1, 'total': 3, 'absent': 1},
                    {'attendance_day__attendance_date__month': 2, 'total': 1, 'absent': 1},
                ]
            if groups == (
                'attendance_day__attendance_date__month',
                'registration__education_service__education_program',
            ):
                return [
                    {
                        'attendance_day__attendance_date__month': 1,
                        'registration__education_service__education_program': 'BLN Level 1',
                        'total': 1,
                        'absent': 0,
                    },
                    {
                        'attendance_day__attendance_date__month': 2,
                        'registration__education_service__education_program': 'BLN Level 1',
                        'total': 1,
                        'absent': 1,
                    },
                    {
                        'attendance_day__attendance_date__month': 1,
                        'registration__education_service__education_program': 'YFS Level 1',
                        'total': 2,
                        'absent': 1,
                    },
                ]
            raise AssertionError(f'Unexpected grouping: {groups!r}')

        with patch(
            'student_registration.mscc.attendance_views._aggregate_attendance',
            side_effect=aggregate_side_effect,
        ) as mock_aggregate:
            view = AttendanceHeatmapViewSet.as_view({'get': 'percentage'})
            response = view(request)

    mock_filter.assert_called_once()
    mock_dates.assert_called_once_with('attendance_day__attendance_date', 'year')

    assert response.status_code == 200
    payload = json.loads(response.content)

    monthly = [entry for entry in payload if entry['record_type'] == 'monthly']
    programme_entries = [entry for entry in payload if entry['record_type'] == 'programme_monthly']

    january = next(entry for entry in monthly if entry['month'] == 1)
    february = next(entry for entry in monthly if entry['month'] == 2)

    assert january['attendance_percentage'] == pytest.approx(66.67, rel=1e-3)
    assert january['present'] == 2
    assert january['absent'] == 1
    assert january['total'] == 3
    assert january['month_name'] == 'January'

    assert february['attendance_percentage'] == 0.0
    assert february['present'] == 0
    assert february['absent'] == 1
    assert february['total'] == 1
    assert february['month_name'] == 'February'

    grouped_programmes = {}
    for entry in programme_entries:
        grouped_programmes.setdefault(entry['programme'], []).append(entry)

    assert set(grouped_programmes.keys()) == {'BLN', 'YFS'}

    bln_entries = sorted(grouped_programmes['BLN'], key=lambda item: item['month'])
    assert [entry['attendance_percentage'] for entry in bln_entries] == [100.0, 0.0]
    assert [entry['month'] for entry in bln_entries] == [1, 2]

    yfs_entries = grouped_programmes['YFS']
    assert [entry['attendance_percentage'] for entry in yfs_entries] == [50.0]
    assert [entry['month'] for entry in yfs_entries] == [1]

    assert all(entry['year'] == 2024 for entry in monthly)
    assert all(entry['available_years'] == '2023,2024' for entry in monthly)
