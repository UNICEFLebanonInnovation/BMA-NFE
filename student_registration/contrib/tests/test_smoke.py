import student_registration.contrib.sites as sites


def test_doc_hint():
    """Ensure the documentation hint exists."""
    assert 'cookiecutter-django' in (sites.__doc__ or '')
