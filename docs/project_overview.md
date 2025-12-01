# Student Registration Compiler Overview

## Project structure
- **Top-level orchestration**
  - `local.yml` defines the Docker services used for local development (PostgreSQL database and Django app) and exposes port 8000 for the web server.
  - `production.yml` describes the production stack, including PostgreSQL, Redis, Gunicorn-backed Django, Nginx, Certbot, and Celery workers/beat schedulers for background tasks.
  - `env.example` lists the environment variables required across environments, such as database credentials, Django settings, Sentry DSN, and Firebase configuration.
  - `requirements/` contains dependency sets for base, local development, production, and testing to keep installations environment-specific.
- **Django project**
  - `student_registration/` holds the Django project code and apps. Notable modules include:
    - `accounts/`, `users/`, and `backends/` for authentication, user profiles, and backend integrations.
    - `students/`, `attendances/`, `mscc/`, `clm/`, and `schools/` encapsulate domain logic for student registration, attendance tracking, MSCC workflows, child learning management, and school data, respectively.
    - `taskapp/` configures Celery for asynchronous processing and periodic tasks.
    - `templates/` and `static/` host the server-rendered UI assets.
    - Middleware helpers (for HSTS, X-Frame options, cache control, lockout protection, and single-session enforcement) live at the project root.
- **Tooling and config**
  - `manage.py` is the Django entry point for administrative commands.
  - `pytest.ini` and `runtests.sh` provide testing defaults.
  - `Procfile` and `web.config` support platform-specific process declarations.

## Key features and components
- **Student registration and account management** via Django apps for accounts, users, and students, enabling authentication and profile handling.
- **Attendance and learning modules** in `attendances/`, `mscc/`, and `clm/` manage attendance logging, MSCC program workflows, and child learning management utilities.
- **School data management** in `schools/` covers school records, creation/edit flows, and autocomplete/location helper views.
- **Background processing** through Celery workers defined in `taskapp/`, with dedicated queues for long-running exports and beat scheduling for periodic jobs.
- **Push notifications** support through Firebase Cloud Messaging configuration variables documented in `env.example` and described in the README for notifying clients when exports complete.
- **Error monitoring** with Sentry via environment configuration for capturing server-side issues.

## Local development setup
1. **Create and populate an environment file**:
   - Copy `env.example` to `.env` or export the required variables in your shell. Provide values for `DJANGO_SECRET_KEY`, database credentials, allowed hosts, email settings, FCM keys, and Sentry DSN as needed.
2. **Install dependencies**:
   - With Python available locally, install packages using `pip install -r requirements/local.txt` to include development helpers like Django Extensions and Debug Toolbar.
3. **Run database migrations**:
   - Apply migrations with `python manage.py migrate` from the repository root.
4. **Create a superuser (optional)**:
   - Execute `python manage.py createsuperuser` to set up an admin account.
5. **Start the development server**:
   - Launch Django with `python manage.py runserver 0.0.0.0:8000` and access the site at http://localhost:8000.

### Docker-based local workflow
1. Build and start the stack with `docker-compose -f local.yml up --build`.
2. The Django app will be available on port 8000, backed by the PostgreSQL service defined in `local.yml`.
3. Use `docker-compose -f local.yml exec django python manage.py migrate` for migrations and similar commands inside the container.

### Common Django management commands
- `python manage.py makemigrations` — generate new migration files based on model changes.
- `python manage.py migrate` — apply pending migrations to the configured database.
- `python manage.py createsuperuser` — create an administrative user for accessing the Django admin site.
- `python manage.py shell` — open a Django-aware Python shell for debugging or ad-hoc tasks.
- `python manage.py collectstatic` — gather static assets into the configured `STATIC_ROOT` for production serving.
- `python manage.py showmigrations` — list migrations and their applied status across installed apps.
- `python manage.py check` — run Django’s system checks to validate configuration and catch common issues.

## Testing
- Run the Django test suite with `pytest` or `py.test` using the configuration in `pytest.ini`.
- Alternatively, use `coverage run manage.py test` to generate coverage data and `coverage html` to build the HTML report.

## Deployment guidance
1. **Prepare environment variables**:
   - Create a `.env` file with production-ready values for database connection, Django secret key, allowed hosts, email providers, Sentry DSN, FCM server key, and Firebase web app settings as outlined in `env.example`.
2. **Build and start production services**:
   - Use `docker-compose -f production.yml up --build -d` to launch PostgreSQL, Redis, the Gunicorn-based Django container, Nginx, Certbot, and Celery workers/beat.
3. **Apply migrations and collect static files**:
   - Run `docker-compose -f production.yml exec django python manage.py migrate` followed by `docker-compose -f production.yml exec django python manage.py collectstatic --noinput`.
4. **Background workers**:
   - Celery worker and beat processes are defined in `production.yml` and start automatically with the stack; ensure Redis is reachable.
5. **TLS certificates**:
   - Certbot in `production.yml` is configured to request certificates for the specified domain; update the domain and email as needed before deployment.

## Process management hints
- `Procfile` supplies process commands for platforms that read process declarations (e.g., Heroku-like environments).
- `web.config` provides IIS configuration when hosting on Windows-based servers.
- For non-container deployments, you can run `gunicorn student_registration.wsgi:application` behind a reverse proxy like Nginx, using the same environment variables and static/media file settings outlined above.
