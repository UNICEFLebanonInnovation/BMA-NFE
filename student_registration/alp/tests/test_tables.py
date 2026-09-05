import pytest
from django.template.loader import get_template

from student_registration.alp.tables import (
    ALPAttendanceTable,
    ALPRegistrationTable,
    ALPTeacherAttendanceTable,
    ALPTeacherTable,
)


@pytest.mark.parametrize(
    "table_class",
    (
        ALPRegistrationTable,
        ALPTeacherTable,
        ALPAttendanceTable,
        ALPTeacherAttendanceTable,
    ),
)
def test_actions_template_loads_its_template_tag_libraries(table_class):
    """Action templates must load their tags independently of the page."""
    get_template(table_class.base_columns["actions"].template_name)


def test_registration_actions_are_the_first_column():
    assert list(ALPRegistrationTable.base_columns)[0] == "actions"
