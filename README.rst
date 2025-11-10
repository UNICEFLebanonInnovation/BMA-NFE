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

Export completion messages are sent via Firebase Cloud Messaging (FCM). Provide your Firebase server key in the ``FCM_SERVER_KEY`` environment variable so that ``student_registration.mscc.tasks`` can deliver notifications. This value is read from ``config/settings/base.py`` and is required for the server to push notifications.

To receive notifications on the client, initialize Firebase with your project's web configuration values and reference them in your frontend code.

Required variables:

- ``FIREBASE_API_KEY``
- ``FIREBASE_AUTH_DOMAIN``
- ``FIREBASE_PROJECT_ID``
- ``FIREBASE_STORAGE_BUCKET``
- ``FIREBASE_MESSAGING_SENDER_ID``
- ``FIREBASE_APP_ID``
- ``FIREBASE_MEASUREMENT_ID``

Example initialization snippet::

    import { initializeApp } from "firebase/app";
    import { getAnalytics } from "firebase/analytics";

    const firebaseConfig = {
        apiKey: "<YOUR_FIREBASE_API_KEY>",
        authDomain: "<YOUR_FIREBASE_AUTH_DOMAIN>",
        projectId: "<YOUR_FIREBASE_PROJECT_ID>",
        storageBucket: "<YOUR_FIREBASE_STORAGE_BUCKET>",
        messagingSenderId: "<YOUR_FIREBASE_MESSAGING_SENDER_ID>",
        appId: "<YOUR_FIREBASE_APP_ID>",
        measurementId: "<YOUR_FIREBASE_MEASUREMENT_ID>",
    };

    const app = initializeApp(firebaseConfig);
    getAnalytics(app);





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
