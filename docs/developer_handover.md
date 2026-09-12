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
For a detailed guide on setting up a local development environment, please refer to the `docs/deployment.md` file. This document provides comprehensive instructions on how to configure the project, including the database and other sensitive information.

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
- **Documentation pages**: The in-app docs are served from `docs/wiki/` (Markdown, `/dashboard/wiki/<page>/`) and `docs/wiki_html/` (HTML, `/dashboard/guide/<page>/`). The two trees are mirrors and are updated by hand — there is no build step, so a page added to one should be added to the other.

## In-app documentation access control
Both documentation routes share one rule, implemented by `_require_wiki_access` in `student_registration/dashboard/views.py`:

- Any signed-in user may read the end user manual (`end_user`), plus the wiki index on the Markdown route.
- Every other page — the administration guide, developer guide and system overview, which describe deployment details and the role/permission model — returns HTTP 404 for non-superusers.
- The sidebar "Wiki" entry is rendered for superusers only; standard users see only "User Guide".

Because the Markdown and HTML trees carry the same content, a restriction added to one route must be added to the other. Keep the rule in the shared helper rather than duplicating it per view, and extend `student_registration/dashboard/tests/test_wiki_access.py` when adding pages.

Keep this guide with the repository so future maintainers have a concise starting point.
