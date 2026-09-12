BMA — NFE Sector Platform
=========================

Case management and service-delivery tracking for UNICEF Lebanon's Non-Formal Education sector.
The repository is historically named *Student Registration Compiler*; the deployed product is the
**BMA NFE Sector platform**.

.. image:: https://img.shields.io/badge/built%20with-Cookiecutter%20Django-ff69b4.svg
     :target: https://github.com/pydanny/cookiecutter-django/
     :alt: Built with Cookiecutter Django

:License: GPLv3

The platform covers three programme modules plus cross-cutting reporting:

=============== ==============================================================================
Module          Scope
=============== ==============================================================================
``mscc``        Makani (MSCC) centers — child registration, service delivery, attendance,
                exports
``alp``         Accelerated Learning Programme — school-scoped registration, teachers,
                attendance, grading, school profile, dashboards
``clm``         Community Learning / bridging programme
``dashboard``   Cross-module analytics, pivot tables, maps and the advanced exporter
=============== ==============================================================================


Documentation
-------------

The Markdown under ``docs/wiki/`` is the source of truth and is also served inside the running
application (``/dashboard/wiki/`` for every signed-in user, ``/dashboard/guide/`` for superusers,
with the End User Manual open to everyone).

Start here:

* ``docs/wiki/index.md`` — documentation home.
* ``docs/wiki/end_user.md`` — end user manual for field staff, coordinators and school focal points.
* ``docs/wiki/admin.md`` — deployment, RBAC, configuration reference, backups, monitoring.
* ``docs/wiki/developer.md`` — architecture, apps, access control, API surface, Celery, testing.
* ``docs/wiki/system_details.md`` — dependency, model and infrastructure snapshot.

Reference and handover material:

* ``docs/ACCESS_CONTROL.md`` — role → view permission matrix.
* ``docs/project_overview.md`` — repository layout, local setup, management commands.
* ``docs/deployment.md`` — deployment and maintenance guide, environment variable reference.
* ``docs/ministry_handover.md`` — end-to-end runbook for Ministry operations teams.
* ``docs/handover_checklist.md`` — go-live checklist.
* ``docs/developer_handover.md`` — concise orientation for new maintainers.
* ``docs/analytics_dashboard.md`` — analytics API design and recommended PostgreSQL indexes.
* ``DOCS_REDESIGN.md`` and ``docs/ui_ux_redesign_proposal.md`` — the UI design system.

After editing any page under ``docs/wiki/``, regenerate the HTML mirror served to administrators::

    $ python docs/build_wiki_html.py

``python docs/build_wiki_html.py --check`` exits non-zero when the mirror is out of date, which makes
it usable as a CI guard.


Settings
--------

Settings live in ``config/settings/`` (``base.py``, ``local.py``, ``test.py``, ``production.py``) and
read configuration from the environment with ``django-environ``. Copy ``env.example`` to ``.env`` as a
starting point; the full variable reference is in ``docs/deployment.md``.

Two variables deserve attention:

* ``DJANGO_SETTINGS_MODULE`` selects the settings module (``config.settings.production`` in production).
* ``DATABASE_URL`` **must** be set explicitly. It is not listed in ``env.example``, and
  ``config/settings/base.py`` currently falls back to a hardcoded value that contains credentials — that
  fallback should not be relied on and the credentials in it should be rotated.

The cookiecutter-django settings background still applies: settings_.

.. _settings: http://cookiecutter-django.readthedocs.io/en/latest/settings.html


Basic Commands
--------------

Setting Up Your Users
^^^^^^^^^^^^^^^^^^^^^

Accounts are created by administrators, not by self-service sign-up. Create an **administrator
account** with::

    $ python manage.py createsuperuser

Ordinary accounts are created from the Django admin. Every account needs both a **group**
(for example ``MSCC_CENTER``, ``ALP_SCHOOL``, ``CLM_Bridging``) and the matching **center, partner or
school** assignment — a user with a group but no assignment sees empty lists everywhere. See
``docs/ACCESS_CONTROL.md`` for the full matrix.

Test coverage
^^^^^^^^^^^^^

Tests run against ``config.settings.test`` (set by ``pytest.ini``) and require PostgreSQL — the models
use PostgreSQL-only field types, so SQLite will not work.

To run the tests, check your test coverage, and generate an HTML coverage report::

    $ pytest
    $ pytest student_registration/alp/tests    # a single app
    $ coverage run manage.py test
    $ coverage html
    $ open htmlcov/index.html

Linting follows ``setup.cfg`` (``flake8``/``pycodestyle``, 120-character lines)::

    $ flake8 .

Live reloading and Sass CSS compilation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

``package.json`` still pins a legacy gulp 3 pipeline. It is not required to run or build the
application — static assets are committed and served directly. See `Live reloading and SASS compilation`_
for the original cookiecutter workflow.

.. _`Live reloading and SASS compilation`: http://cookiecutter-django.readthedocs.io/en/latest/live-reloading-and-sass-compilation.html


Celery
^^^^^^

This app comes with Celery.
Periodic tasks are managed via ``django-celery-beat`` and stored in the
database.  You can create schedules from the Django admin interface under
``Periodic tasks`` and select any available Celery task by name. Task results are
stored via ``django-celery-results`` and are browsable in the admin.

To run a celery worker (and the beat scheduler):

.. code-block:: bash

    cd student_registration
    celery -A student_registration.taskapp worker -l info
    celery -A student_registration.taskapp beat -l info

Please note: For Celery's import magic to work, it is important *where* the celery commands are run. If you are in the same folder with *manage.py*, you should be right.

Long running export tasks are routed to a dedicated ``mscc_export`` queue. Run a
worker for that queue with limited concurrency to avoid heavy exports running in
parallel:

.. code-block:: bash

    celery -A student_registration.taskapp worker -Q mscc_export --concurrency=1 -l info

Push Notifications
^^^^^^^^^^^^^^^^^^

Export completion messages are sent via Firebase Cloud Messaging (FCM).

Server side, ``student_registration/backends/utils.py`` initialises ``firebase-admin`` from a
**service-account JSON file at** ``utility/firebase-creds.json``. The ``FCM_SERVER_KEY`` environment
variable still listed in ``env.example`` is obsolete and is **not read anywhere in the codebase**.

.. warning::

   A real service-account private key is currently committed at ``utility/firebase-creds.json``. It
   should be rotated in the Firebase console and supplied at deploy time from a secret store or a
   mounted file, not from version control.

Browser side, the client registers a device token through the ``save_fcm_token`` endpoint; tokens are
stored in the ``WebPushToken`` model. A user with no registered token simply receives no push — the
export still completes and remains downloadable. The Firebase web configuration is currently hardcoded
in ``student_registration/static/js/firebase-messaging.js`` and
``student_registration/static/firebase-messaging-sw.js``; the service worker
``firebase-messaging-sw.js`` handles background pushes.


Sentry
^^^^^^

Sentry is an error logging aggregator service. You can sign up for a free account at  https://sentry.io/signup/?code=cookiecutter  or download and host it yourself.
The system is setup with reasonable defaults, including 404 logging and integration with the WSGI application.

You must set ``DJANGO_SENTRY_DSN`` in production. ``azure-monitor-opentelemetry`` is also available and
is configured through the ``OTEL_*`` environment variables.


API
---

The REST API is built with Django REST Framework and documents itself through ``drf-spectacular``:

============================  ==========================
URL                           Purpose
============================  ==========================
``/api/schema/``              OpenAPI 3 schema (YAML)
``/api/docs/``                Swagger UI
``/api/schema/redoc/``        ReDoc UI
============================  ==========================

All endpoints require an authenticated user.


Deployment
----------

See ``docs/deployment.md`` for the full guide, and ``docs/ministry_handover.md`` for the operations
runbook. In short::

    $ docker compose -f production.yml up --build -d
    $ docker compose -f production.yml exec django python manage.py migrate
    $ docker compose -f production.yml exec django python manage.py collectstatic --noinput
    $ docker compose -f production.yml exec django python manage.py compilemessages

Docker
^^^^^^

See detailed `cookiecutter-django Docker documentation`_.

.. _`cookiecutter-django Docker documentation`: http://cookiecutter-django.readthedocs.io/en/latest/deployment-with-docker.html


Translations
------------

The interface ships in English and Arabic, with a right-to-left layout for Arabic. Compiled catalogues
(``*.mo``) are deliberately not committed, so compile them as part of every deployment::

    $ ./manage.py compilemessages
