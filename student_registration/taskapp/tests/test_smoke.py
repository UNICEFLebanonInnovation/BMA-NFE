from student_registration.taskapp.celery import CeleryConfig


def test_app_name():
    """Celery app should use the correct name."""
    assert CeleryConfig.name == 'student_registration.taskapp'
