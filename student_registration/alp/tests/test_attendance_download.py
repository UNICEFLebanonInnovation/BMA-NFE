from pathlib import Path
from unittest import TestCase


class ALPAttendanceDownloadTest(TestCase):
    def test_download_button_is_wired_to_csv_export(self):
        alp_root = Path(__file__).resolve().parents[1]
        template_root = alp_root.parent / "templates" / "alp"
        static_root = alp_root.parent / "static" / "js" / "alp"

        page = (template_root / "attendance.html").read_text(encoding="utf-8")
        children = (template_root / "attendance_children.html").read_text(encoding="utf-8")
        script = (static_root / "attendance.js").read_text(encoding="utf-8")

        self.assertIn('id="download_attendance"', page)
        self.assertIn('data-child-name="{{ item.child_fullname }}"', children)
        self.assertIn("function downloadAttendanceCsv()", script)
        self.assertIn("new Blob([csv]", script)
        self.assertIn("link.download = 'alp_attendance_'", script)
