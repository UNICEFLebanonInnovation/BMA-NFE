"""Source timestamps work with the existing USE_TZ=False project settings."""
from datetime import datetime
from django.test import SimpleTestCase, override_settings
from django.utils import timezone
from ..identity import source_timestamp


class SourceTimestampTests(SimpleTestCase):
    @override_settings(USE_TZ=False, TIME_ZONE='Asia/Beirut')
    def test_offset_is_normalized_for_naive_database_fields(self):
        self.assertEqual(source_timestamp('2026-10-18T09:00:00Z'),
                         datetime(2026, 10, 18, 12))

    @override_settings(USE_TZ=True)
    def test_timezone_aware_database_fields_keep_offset(self):
        self.assertTrue(timezone.is_aware(source_timestamp('2026-10-18T09:00:00Z')))

    @override_settings(USE_TZ=False)
    def test_wire_timestamp_without_offset_is_still_rejected(self):
        with self.assertRaisesRegex(ValueError, 'must include a timezone'):
            source_timestamp('2026-10-18T09:00:00')
