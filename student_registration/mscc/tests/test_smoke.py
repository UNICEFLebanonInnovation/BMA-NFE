import pytest
from django.core.exceptions import ValidationError
from django import forms
from student_registration.mscc.utils import validate_date, TrimmedDateField


def test_validate_date_ok():
    assert validate_date('2024-05-01').isoformat() == '2024-05-01'


def test_validate_date_strip_ok():
    assert validate_date('2025-02-11 ').isoformat() == '2025-02-11'


def test_validate_date_error():
    with pytest.raises(ValidationError):
        validate_date('invalid')


class _DummyForm(forms.Form):
    session_date = TrimmedDateField(required=False)


def test_trimmed_date_field_accepts_spaces():
    form = _DummyForm({'session_date': '2025-02-11 '})
    assert form.is_valid()
    assert form.cleaned_data['session_date'].isoformat() == '2025-02-11'
