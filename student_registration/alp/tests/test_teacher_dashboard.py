from django.template.loader import get_template
from django.test import SimpleTestCase


class ALPTeacherDashboardTemplateTests(SimpleTestCase):
    def test_teacher_dashboard_has_one_content_block(self):
        template = get_template('alp/dashboard_teacher.html')

        content_blocks = [
            node for node in template.template.nodelist
            if getattr(node, 'name', None) == 'content'
        ]

        self.assertEqual(len(content_blocks), 1)

    def test_teacher_dashboard_does_not_include_attendance_dashboard_assets(self):
        template = get_template('alp/dashboard_teacher.html')
        source = template.template.source

        self.assertNotIn('teacher-attendance-dashboard.css', source)
        self.assertNotIn('teacher_attendance_dashboard.js', source)
