from student_registration.backends.djqscsv import _append_datestamp


def test_append_datestamp():
    """Check filename datestamp helper."""
    stamped = _append_datestamp('data.csv')
    assert stamped.startswith('data_') and stamped.endswith('.csv')
