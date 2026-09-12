# Developer handover guide

**Revision: September 2026**

This document orients new maintainers to the core components of the BMA NFE Sector codebase (repository
name: *Student Registration Compiler*) so they can troubleshoot and extend the project confidently. For the
full architecture reference see [`docs/wiki/developer.md`](./wiki/developer.md).

## Architecture at a glance
- **Stack**: Django 5.2 on Python 3.11+, PostgreSQL via `psycopg` 3, Redis for cache and Celery broker, DRF + `drf-spectacular` for the API, Bootstrap 5 server-rendered templates.
- **Django apps**: Domain logic lives in `student_registration/`; `LOCAL_APPS` in `config/settings/base.py` is the authoritative list.
  - `users/`, `backends/`: custom user model, group helpers, storage backends, Firebase push helpers. `accounts/` is installed only in production settings.
  - `child/`: the shared `Child` record used by both MSCC and ALP.
  - `mscc/`, `alp/`, `clm/`, `students/`, `attendances/`, `schools/`, `locations/`: the domain apps. `alp/` (the Accelerated Learning Programme) is the newest and most actively developed module.
  - `dashboard/`: analytics endpoints, pivot tables, maps, the advanced exporter, and the views that serve this documentation inside the app.
  - `taskapp/`: Celery configuration and task discovery.
  - Cross-cutting middleware such as `cache_control_middleware.py`, `hsts_middleware.py`, `lockout_middleware.py` and `one_session.py` lives at the project root — but check `config/settings/` before assuming a given one is enabled. `AutoLogout`, `CacheControl`, `HSTS` and `XFrame` are added in `production.py`; `OneSessionPerUserMiddleware` is commented out and `StudentLockoutMiddleware` is not registered at all.
- **Celery workers**: Asynchronous tasks run through `student_registration.taskapp`. Long-running MSCC exports are offloaded to dedicated queues; see `student_registration/mscc/tasks.py`.
- **Views and templates**: Server-rendered pages live under `student_registration/templates/`; client assets live under `student_registration/static/`.

## Local development quickstart
For a detailed guide on setting up a local development environment, please refer to the `docs/deployment.md` file. This document provides comprehensive instructions on how to configure the project, including the database and other sensitive information.

## Background processing
- **Celery bootstrap**: `student_registration/taskapp/celery.py` loads Django settings, autodiscovers tasks across installed apps, and registers logging/monitoring hooks (Opbeat where enabled).
- **MSCC exports**: `student_registration/mscc/tasks.py` contains threaded exporters that read from database views (`vw_mscc_child`, `vw_mscc_data`, `mscc_followupservice`), write CSV/XLSX output into a ZIP file, and persist it via `ExportStorage`. A push notification is sent via Firebase when a file is ready or if the export fails. Long exports should use the `mscc_export` queue to avoid contention with other tasks.
- **Queue selection**: Configure queue names and worker counts via `CELERY_` settings. To throttle heavy export jobs, run `celery -A student_registration.taskapp worker -Q mscc_export --concurrency=1 -l info`.

## Troubleshooting tips
- **Database connections in threads**: Tasks that spawn threads call `close_old_connections()` before and after execution to avoid stale DB connections.
- **Push notifications**: Export tasks call `send_push_to_web` in `student_registration/backends/utils.py`, which initialises `firebase-admin` from the service-account JSON at `utility/firebase-creds.json`. A missing or invalid credentials file surfaces as a runtime error when an export finishes. The `FCM_SERVER_KEY` environment variable is obsolete and is not read anywhere. A user with no registered `WebPushToken` simply gets no notification — the export still completes.
- **Session enforcement**: Unexpected logouts in production are usually `AUTO_LOGOUT_DELAY` (30 minutes of inactivity) in `config/settings/production.py`. `student_registration/one_session.py` would enforce a single active session per user, but it is currently commented out of `EXTRA_MIDDLEWARE`.
- **ALP data appearing empty**: `alp/utils.filter_by_school()` returns an empty queryset when the user has no `school_id`, and does not exempt superusers. Check the user's school assignment and `ALP_SCHOOL` group membership before debugging further.
- **Error tracking**: Sentry is enabled when `DJANGO_SENTRY_DSN` is present. Check environment variables before debugging missing alerts.

## Where to add new features
- **API/UI changes**: Extend the relevant domain app (`mscc`, `alp`, `clm`, `students`, `attendances`, `schools`) and update templates under `student_registration/templates/`. Every new view needs a group check and queryset scoping; record it in `docs/ACCESS_CONTROL.md`.
- **Background tasks**: Add Celery tasks inside the corresponding app’s `tasks.py`. Ensure workers are subscribed to any new queues you introduce.
- **Deploy artifacts**: Update `requirements/` sets and `production.yml`/`local.yml` when new services or dependencies are required.

## Documentation
- The Markdown under `docs/wiki/` is the source of truth and is served in-app at `/dashboard/wiki/`.
- `docs/wiki_html/` is the HTML mirror served at `/dashboard/guide/` (superusers only, except the end user manual).
- Regenerate the mirror with `python docs/build_wiki_html.py` after editing any Markdown page.

## Known issues worth addressing
- `config/settings/base.py` carries a hardcoded `DATABASE_URL` default containing credentials.
- A Firebase service-account private key is committed at `utility/firebase-creds.json`.
- `dev.env` contains a committed `DJANGO_SECRET_KEY`.
- `WikiPageView` (`/dashboard/wiki/`) has no superuser check, while `WikiGuidePageView` (`/dashboard/guide/`) does — technical pages are therefore readable by any signed-in user through the Markdown route.
- `student_registration/templates/alp/attendance_list.html` is unreferenced by any view and reverses a URL name (`alp:attendance_add`) that does not exist.

Keep this guide with the repository so future maintainers have a concise starting point.
