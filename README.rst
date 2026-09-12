Student Registration Compiler
=============================

Simple, interactive and online student registration.

.. image:: https://img.shields.io/badge/built%20with-Cookiecutter%20Django-ff69b4.svg
     :target: https://github.com/pydanny/cookiecutter-django/
     :alt: Built with Cookiecutter Django

.. image:: https://travis-ci.org/UNICEFLebanonInnovation/Compiler.svg?branch=develop
    :target: https://travis-ci.org/UNICEFLebanonInnovation/Compiler
    
.. image:: https://coveralls.io/repos/github/UNICEFLebanonInnovation/Compiler/badge.svg?branch=develop
    :target: https://coveralls.io/github/UNICEFLebanonInnovation/Compiler?branch=develop

:License: GPLv3


Handover documentation
-----------------------

For Ministry operations teams, two documents provide explicit deployment and support steps:

* ``docs/ministry_handover.md`` — end-to-end runbook covering prerequisites, configuration, production deployment, routine operations, backup/restore, and disaster recovery.
* ``docs/handover_checklist.md`` — checklist to confirm the platform is production-ready (environment, monitoring, backups, and ownership).
* ``docs/developer_handover.md`` — technical overview for maintainers that explains key Django apps, Celery usage, background exports, and how to set up a development environment.

A third document, ``docs/deployment.md``, has been added to provide a more detailed guide for deploying and maintaining the project. This includes comprehensive instructions on environment setup, database configuration, and running the application in a production environment. This new document consolidates and clarifies the deployment process, making it easier for new developers to get started.

Settings
--------

Moved to settings_.

.. _settings: http://cookiecutter-django.readthedocs.io/en/latest/settings.html

Basic Commands
--------------

Setting Up Your Users
^^^^^^^^^^^^^^^^^^^^^

* To create a **normal user account**, just go to Sign Up and fill out the form. Once you submit it, you'll see a "Verify Your E-mail Address" page. Go to your console to see a simulated email verification message. Copy the link into your browser. Now the user's email should be verified and ready to go.

* To create an **superuser account**, use this command::

    $ python manage.py createsuperuser

For convenience, you can keep your normal user logged in on Chrome and your superuser logged in on Firefox (or similar), so that you can see how the site behaves for both kinds of users.

Test coverage
^^^^^^^^^^^^^

To run the tests, check your test coverage, and generate an HTML coverage report::

    $ coverage run manage.py test
    $ coverage html
    $ open htmlcov/index.html

Running tests with py.test
~~~~~~~~~~~~~~~~~~~~~~~~~~

::

  $ py.test

Live reloading and Sass CSS compilation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Moved to `Live reloading and SASS compilation`_.

.. _`Live reloading and SASS compilation`: http://cookiecutter-django.readthedocs.io/en/latest/live-reloading-and-sass-compilation.html



Celery
^^^^^^

This app comes with Celery.
Periodic tasks are managed via ``django-celery-beat`` and stored in the
database.  You can create schedules from the Django admin interface under
``Periodic tasks`` and select any available Celery task by name.

To view execution history, the project records each run in ``Task run logs``
which is also accessible from the admin site.

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

Export completion messages are sent via Firebase Cloud Messaging (FCM). The server side
uses the ``firebase-admin`` SDK, which authenticates with a Google service-account JSON
file rather than a legacy server key.

That file contains a private key and is **not** kept in version control. Supply it at
deploy time -- mount it into the container or write it out from a secret store -- and
point the application at it::

    FIREBASE_CREDENTIALS_FILE=/run/secrets/firebase-creds.json

When ``FIREBASE_CREDENTIALS_FILE`` is unset, the application falls back to
``utility/firebase-creds.json`` relative to the project root. If the file is missing or
unreadable, push notifications are skipped and a warning is logged rather than raising.

The client-side Firebase web configuration (API key, sender ID, app ID and so on) is not
read from the environment. It lives in ``student_registration/static/js/firebase-messaging.js``
and ``student_registration/static/firebase-messaging-sw.js``. These values are public
identifiers by design; access is controlled by Firebase Security Rules, not by keeping
them secret. Edit those two files to point the frontend at a different Firebase project.





Sentry
^^^^^^

Sentry is an error logging aggregator service. You can sign up for a free account at  https://sentry.io/signup/?code=cookiecutter  or download and host it yourself.
The system is setup with reasonable defaults, including 404 logging and integration with the WSGI application.

You must set the DSN url in production.


Deployment
----------

The following details how to deploy this application.



Docker
^^^^^^

See detailed `cookiecutter-django Docker documentation`_.

.. _`cookiecutter-django Docker documentation`: http://cookiecutter-django.readthedocs.io/en/latest/deployment-with-docker.html



Translations
------------

./manage.py compilemessages
