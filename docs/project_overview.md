# BMA — NFE Sector Platform Overview

**Revision: September 2026**

The repository is historically named *Student Registration Compiler*; the deployed product is the
**BMA NFE Sector platform**.

## Project structure
- **Top-level orchestration**
  - `local.yml` defines the Docker services used for local development (PostgreSQL database and Django app) and exposes port 8000 for the web server.
  - `production.yml` describes the production stack, including PostgreSQL, Redis, Gunicorn-backed Django, Nginx, Certbot, and Celery workers/beat schedulers for background tasks.
  - `env.example` lists the environment variables required across environments, such as database credentials, Django settings, Sentry DSN, and Firebase configuration.
  - `requirements/` contains dependency sets for base, local development, production, and testing to keep installations environment-specific.
- **Django project**
  - `student_registration/` holds the Django project code and apps. `LOCAL_APPS` in
    `config/settings/base.py` is the authoritative list:
    - `users/` and `backends/` for the custom user model, group helpers, storage backends and Firebase push helpers. `accounts/` holds account signal handlers and is added to `INSTALLED_APPS` only by `config/settings/production.py`.
    - `child/` holds the shared `Child` record (identity, caregivers, ID documents) that both MSCC and ALP build on.
    - `mscc/`, `alp/`, `clm/`, `students/`, `attendances/` and `schools/` encapsulate the domain logic for Makani workflows, the Accelerated Learning Programme, the bridging programme, legacy student/teacher records, attendance tracking and school data respectively.
    - `locations/` holds `Location`, `LocationType` and `Center` reference data.
    - `dashboard/` holds cross-module analytics endpoints, pivot tables, maps, the advanced exporter, and the views that serve this documentation inside the application.
    - `taskapp/` configures Celery for asynchronous processing and periodic tasks.
    - `templates/` and `static/` host the server-rendered UI assets.
    - Middleware helpers (HSTS, X-Frame options, cache control, auto-logout, lockout protection and single-session enforcement) live at the project root. Only some are wired into `MIDDLEWARE` — see the middleware table in `docs/wiki/developer.md` for which ones are actually enabled.
- **Tooling and config**
  - `manage.py` is the Django entry point for administrative commands.
  - `pytest.ini` and `runtests.sh` provide testing defaults.
  - `Procfile` and `web.config` support platform-specific process declarations.

## Key features and components
- **Beneficiary registration and account management** via the `users`, `child`, `mscc`, `alp` and `students` apps, covering authentication, group-based authorization and profile handling.
- **MSCC (Makani) workflows** in `mscc/`: a multi-step registration wizard, service delivery forms (education, health and nutrition, youth, PSS, inclusion, digital, recreational, LEGO, referrals and follow-ups), attendance and dashboards.
- **ALP (Accelerated Learning Programme)** in `alp/`: school-scoped registrations with consent-form upload, teacher records, child and teacher attendance, dynamic grading driven by configurable grading definitions, an editable school profile, and five dashboards. All ALP data is filtered to the school linked to the user account.
- **CLM bridging workflows** in `clm/` for community learning classes, assessments and follow-ups.
- **Attendance** in `attendances/` plus per-module attendance views, with heatmaps and CSV/Excel downloads.
- **School and location data** in `schools/` and `locations/`, including autocomplete and geo endpoints that feed the maps.
- **Analytics** in `dashboard/`: trend, breakdown and cross-tab endpoints, pivot tables, chart builder, center and school maps, and an advanced background exporter.
- **Background processing** through Celery workers defined in `taskapp/`, with a dedicated `mscc_export` queue for long-running exports and beat scheduling for periodic jobs.
- **Push notifications** through Firebase Cloud Messaging. The server uses the `firebase-admin` service account at `utility/firebase-creds.json` — the `FCM_SERVER_KEY` variable still present in `env.example` is obsolete and is not read by the application.
- **Error monitoring** with Sentry (`DJANGO_SENTRY_DSN`) and Azure Monitor / OpenTelemetry.
- **In-app documentation**: the files under `docs/wiki/` and `docs/wiki_html/` are served to signed-in users at `/dashboard/wiki/` and `/dashboard/guide/`.

## Local development setup
1. **Create and populate an environment file**:
   - Copy `env.example` to `.env` or export the required variables in your shell. Provide values for `DATABASE_URL`, `DJANGO_SECRET_KEY`, allowed hosts, email settings, and the Sentry DSN as needed.
   - Always set `DATABASE_URL` explicitly. `config/settings/base.py` currently falls back to a hardcoded default that contains credentials; that default should not be used and the credentials in it should be rotated.
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
- Run the Django test suite with `pytest` using the configuration in `pytest.ini` (which sets `DJANGO_SETTINGS_MODULE=config.settings.test`).
- Run a single module's tests with, for example, `pytest student_registration/alp/tests`.
- Alternatively, use `coverage run manage.py test` to generate coverage data and `coverage html` to build the HTML report.
- A PostgreSQL database is required; the models use PostgreSQL-only field types, so SQLite will not work.

## Deployment guidance
1. **Prepare environment variables**:
   - Create a `.env` file with production-ready values for `DATABASE_URL`, `DJANGO_SECRET_KEY`, `DJANGO_ALLOWED_HOSTS`, `DJANGO_SETTINGS_MODULE=config.settings.production`, email providers and `DJANGO_SENTRY_DSN`, as outlined in `env.example`.
   - Provide the Firebase service-account file at `utility/firebase-creds.json` if push notifications are required. The `FCM_SERVER_KEY` and `FIREBASE_*` entries in `env.example` are obsolete and are not read by the application.
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

## Documentation map
- `docs/wiki/index.md` — entry point for the in-app wiki (end user, administrator and developer guides).
- `docs/wiki/end_user.md` — the end user manual, also served in the application.
- `docs/wiki/developer.md` — architecture, apps, access control, API surface, Celery and testing.
- `docs/wiki/admin.md` — deployment, RBAC, configuration reference, backups and monitoring.
- `docs/wiki/system_details.md` — dependency, model and infrastructure snapshot.
- `docs/ACCESS_CONTROL.md` — role → view permission matrix.
- `docs/analytics_dashboard.md` — analytics API design and recommended indexes.
- `docs/deployment.md` — deployment and maintenance guide.
- After editing anything under `docs/wiki/`, run `python docs/build_wiki_html.py` to refresh the HTML mirror served to administrators.

## Handover package
- See `docs/ministry_handover.md` for a detailed runbook that Ministry operators can follow to deploy, maintain, and recover the system.
- Use `docs/handover_checklist.md` to confirm all operational, security, and ownership prerequisites are satisfied before go-live.
