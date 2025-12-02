# Developer handover guide

This document orients new maintainers to the core components of the Student Registration Compiler codebase so they can troubleshoot and extend the project confidently.

## Architecture at a glance
- **Django apps**: Domain logic lives in `student_registration/`.
  - `accounts/`, `users/`, `backends/`: authentication, roles, and integration helpers.
  - `students/`, `attendances/`, `mscc/`, `clm/`, `schools/`: core feature areas for registrations, attendance logging, MSCC workflows, learning content, and school data.
  - `taskapp/`: Celery configuration and task discovery.
  - Cross-cutting middleware such as `cache_control_middleware.py`, `lockout_middleware.py`, and `one_session.py` enforce security and session hygiene.
- **Celery workers**: Asynchronous tasks run through `student_registration.taskapp`. Long-running MSCC exports are offloaded to dedicated queues; see `student_registration/mscc/tasks.py`.
- **Views and templates**: Server-rendered pages live under `student_registration/templates/`; client assets live under `student_registration/static/`.

## Local development quickstart
1. **Environment**: Copy `env.example` to `.env` and fill in Django, database, Redis, email, FCM, and Sentry settings. Use `DJANGO_SETTINGS_MODULE=config.settings.local` during local work.
2. **Dependencies**: Install Python packages with `pip install -r requirements/local.txt`. Node/Gulp assets are optional for backend-only changes.
3. **Database**: Run `python manage.py migrate` and create a superuser with `python manage.py createsuperuser`.
4. **Run the stack**:
   - **Native**: `python manage.py runserver 0.0.0.0:8000`.
   - **Docker**: `docker compose -f local.yml up --build` (web app on port 8000). Use `docker compose -f local.yml exec django <command>` for management commands.
5. **Testing**: Run `pytest` or `coverage run manage.py test`; see `pytest.ini` for defaults.

## Background processing
- **Celery bootstrap**: `student_registration/taskapp/celery.py` loads Django settings, autodiscovers tasks across installed apps, and registers logging/monitoring hooks (Opbeat where enabled).
- **MSCC exports**: `student_registration/mscc/tasks.py` contains threaded exporters that read from database views (`vw_mscc_child`, `vw_mscc_data`, `mscc_followupservice`), write CSV/XLSX output into a ZIP file, and persist it via `ExportStorage`. A push notification is sent via Firebase when a file is ready or if the export fails. Long exports should use the `mscc_export` queue to avoid contention with other tasks.
- **Queue selection**: Configure queue names and worker counts via `CELERY_` settings. To throttle heavy export jobs, run `celery -A student_registration.taskapp worker -Q mscc_export --concurrency=1 -l info`.

## Troubleshooting tips
- **Database connections in threads**: Tasks that spawn threads call `close_old_connections()` before and after execution to avoid stale DB connections.
- **Push notifications**: Export tasks call `send_push_to_web` with Firebase settings. Missing `FCM_SERVER_KEY` will surface as runtime errors during export completion.
- **Session enforcement**: If users report being logged out unexpectedly, review `student_registration/one_session.py` to confirm session records are cleaned up correctly.
- **Error tracking**: Sentry is enabled when `DJANGO_SENTRY_DSN` is present. Check environment variables before debugging missing alerts.

## Where to add new features
- **API/UI changes**: Extend the relevant domain app (`students`, `attendances`, `mscc`, `clm`, `schools`) and update templates under `student_registration/templates/`.
- **Background tasks**: Add Celery tasks inside the corresponding app’s `tasks.py`. Ensure workers are subscribed to any new queues you introduce.
- **Deploy artifacts**: Update `requirements/` sets and `production.yml`/`local.yml` when new services or dependencies are required.

Keep this guide with the repository so future maintainers have a concise starting point.
