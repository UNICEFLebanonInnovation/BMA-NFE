# Testing Guide

## Prerequisites

Install the application and test dependencies in an isolated Python environment:

```bash
pip install -r requirements/test.txt -r requirements/base.txt
```

The project models use PostgreSQL-specific fields, so the Django suite requires
a PostgreSQL test database. Set `DATABASE_URL` to a database account permitted
to create and drop a test database. Never point test execution at a production
database account.

```bash
export DATABASE_URL=postgresql://user:password@localhost:5432/bma_test_host
export DJANGO_SETTINGS_MODULE=config.settings.test
```

## Test commands

Run the complete Django suite with coverage:

```bash
./run_tests.sh
```

Run only the shared QA foundation tests:

```bash
./run_tests.sh student_registration.tests
```

Run the same tests directly through Django:

```bash
python manage.py test student_registration.tests
```

Run them through pytest:

```bash
pytest student_registration/tests
```

The shared QA factories are in `student_registration/tests/factories.py`. They
create minimal, valid users, partners, locations, centers, children, rounds,
and registrations. `DataQualityReviewerFactory` creates a user in the dedicated
`DATA_QUALITY_REVIEWER` group for future permission tests.

## Scope boundaries

The QA suite will test export business logic directly, including logic normally
invoked by a background task. General Celery broker, routing, retry, worker, and
queue-infrastructure testing remains outside the project scope.
