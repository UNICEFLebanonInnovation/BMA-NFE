# Developer Guide: BMA — NFE Sector Platform

**Revision: September 2026**

Welcome to the **Developer Guide**. This document details the technical architecture, core Django applications, and the frontend ecosystem, providing context for maintaining and extending the platform.

---

## 1. Codebase Architecture Overview

The system is a monolithic Django application designed for high operational data throughput.

| Layer | Technology |
|---|---|
| Framework | Django 5.2 (`django==5.2.7`), Python 3.11+ |
| Database | PostgreSQL, accessed through `psycopg` 3 |
| Cache / broker | Redis (`django-redis`, Celery broker) |
| API | Django REST Framework with `drf-spectacular` schema generation |
| Async | Celery 5.5 with `django-celery-beat` (schedules) and `django-celery-results` (result backend) |
| UI | Server-rendered Django templates, Bootstrap 5.3, vanilla JS, `django-tables2`, `django-filter`, `django-crispy-forms` |
| Admin | `django-jazzmin` skin over Django admin |
| Object storage | Azure Blob Storage via `django-storages` / `azure-storage-blob` |
| Deployment | Docker Compose (`local.yml`, `production.yml`), Gunicorn behind Nginx |

Settings live in `config/settings/` and are split into `base.py`, `local.py`, `test.py` and `production.py`. Configuration is read from the environment with `django-environ`; `DJANGO_SETTINGS_MODULE` selects the module.

---

## 2. Core Django Apps

`LOCAL_APPS` in `config/settings/base.py` is the authoritative list. Domain code is organized as:

| App | Responsibility |
|---|---|
| `users/` | Custom `User` model, group helpers (`has_group`), login routing, FCM token registration, web push tokens |
| `accounts/` | Account signal handlers — **added to `INSTALLED_APPS` only in `production.py`** |
| `child/` | The shared `Child` record (identity, caregivers, ID documents) reused by MSCC and ALP |
| `mscc/` | Makani (MSCC) registrations, service delivery forms, attendance, dashboards, background exports |
| `alp/` | Accelerated Learning Programme — school-scoped registrations, teachers, attendance, grading, dashboards |
| `clm/` | Bridging / Community Learning programme workflows |
| `students/` | Legacy student and `Teacher` models plus shared file-serving helpers |
| `attendances/` | Shared attendance models and views |
| `schools/` | School records, sections, autocomplete and school API viewsets |
| `locations/` | `Location`, `LocationType`, `Center` reference data and autocompletes |
| `dashboard/` | Cross-module analytics endpoints, pivot tables, chart builder, maps, the advanced exporter, and the in-app documentation views |
| `backends/` | Storage backends and integration helpers, including the Firebase push helpers |
| `taskapp/` | Celery app configuration and task autodiscovery (registered as `student_registration.taskapp.celery.CeleryConfig`) |
| `contrib/` | Holds relocated `sites` migrations (`MIGRATION_MODULES`); not an installed app |

### Cross-cutting middleware

`MIDDLEWARE` in `base.py` is deliberately small. Production adds more in `production.py` through `EXTRA_MIDDLEWARE`:

| Middleware | Where it is enabled | Purpose |
|---|---|---|
| `user_activity.UserActivityMiddleware` | all environments | Records last-seen activity per user |
| `whitenoise.middleware.WhiteNoiseMiddleware` | production | Static file serving |
| `middleware.AutoLogout` | production | Logs users out after `AUTO_LOGOUT_DELAY` (30 minutes) |
| `cache_control_middleware.CacheControlMiddleware` | production | No-store headers on authenticated pages |
| `hsts_middleware.HSTSMiddleware` | production | HSTS header |
| `xframe_middleware.XFrameMiddleware` | production | Frame-ancestors protection |
| `one_session.OneSessionPerUserMiddleware` | **currently commented out** | Would enforce one active session per user |
| `lockout_middleware.StudentLockoutMiddleware` | **not registered** | Legacy `django-lockout` hook; the dependency is commented out of `requirements/base.txt`. Failed-login throttling is handled by allauth's `ACCOUNT_RATE_LIMITS` instead |

> When you document or rely on one of these, check the settings module first — several exist in the tree but are not wired up.

---

## 3. Database Schema & PostgreSQL Optimizations

The system leverages PostgreSQL-specific features heavily (`ArrayField`, `JSONField`), meaning **SQLite is not supported for development or testing**.

### Key patterns
*   **ArrayField & JSONField**: Used in `Registration`, `Assessment`, `School`, `ALPRegistration` and `ALPGrading` to handle variable data structures without excessive join tables. `ALPGrading.grading_data` in particular stores a subject → score map keyed by `ALPGradingDefinition` id, so subjects can change without a migration.
*   **Analytics Indexing**: Complex queries (like the Wellbeing Dashboard) rely on specific indexes — see [`docs/analytics_dashboard.md`](../analytics_dashboard.md) for the recommended `CREATE INDEX CONCURRENTLY` statements.
*   **Aggregations**: Use Django's `NullIf` to safely handle potential division-by-zero errors when calculating educational improvements.
*   **Age Bucketing**: Advanced ORM usage (`Case/When` + `ExtractYear(Now())`) groups beneficiaries into analytical cohorts dynamically.
*   **Soft deletes**: `Registration` and `ALPRegistration` carry `deleted` / `deleted_by`; always filter `deleted=False` in reporting queries.

An ER diagram of the schema is committed as `schema.png` at the repository root.

---

## 4. Access Control

Authorization is group-based and layered:

1. **Group membership** — `braces.views.GroupRequiredMixin` (`group_required = [...]`) on class-based views, and the `has_group(user, name)` helper in `student_registration/users/templatetags/custom_tags.py` for views and templates.
2. **Queryset scoping** — views narrow their querysets to the user's `center`, `partner` or `school`. In ALP this is centralized in `alp/utils.filter_by_school()`, which returns an empty queryset when the user has no school and deliberately does **not** exempt privileged users.
3. **Edit gating** — `alp/views.ALPEditPermissionMixin` raises `PermissionDenied` for superusers so that site administrators keep read-only access to school-owned data.
4. **Template filtering** — action buttons are hidden with `{% if request.user|has_group:"…" %}`.

The full role → view matrix is maintained in [`docs/ACCESS_CONTROL.md`](../ACCESS_CONTROL.md). Keep it in sync when you add a view.

---

## 5. API & URL Surface

Routes are declared in `config/urls.py` and per-app `urls.py` modules.

| Prefix | App | Notes |
|---|---|---|
| `/mscc/` | `mscc` | Registrations, services, attendance, exports, dashboards |
| `/alp/` | `alp` | ALP registrations, teachers, attendance, grading, school profile, dashboards |
| `/clm/` | `clm` | Bridging programme |
| `/students/`, `/attendances/`, `/schools/`, `/locations/` | respective apps | Reference data and legacy flows |
| `/dashboard/` | `dashboard` | Analytics JSON endpoints, pivot data, maps, advanced exporter, in-app documentation |
| `/api/` | DRF router | `schools`, `sections`, `teacher`, `locations`, `attendance-heatmap-data` viewsets |
| `/accounts/` | `allauth` | Login, logout, password change |

### Machine-readable API schema

`drf-spectacular` is wired up, so the API documents itself:

| URL | Purpose |
|---|---|
| `/api/schema/` | OpenAPI 3 schema (YAML) |
| `/api/docs/` | Swagger UI |
| `/api/schema/redoc/` | ReDoc UI |

---

## 6. Frontend Ecosystem

The platform was modernized from an older jQuery/ArchitectUI stack to a lighter Bootstrap 5 architecture. The design rules and rationale are captured in [`DOCS_REDESIGN.md`](../../DOCS_REDESIGN.md) and [`docs/ui_ux_redesign_proposal.md`](../ui_ux_redesign_proposal.md).

### Key implementation patterns
*   **Entry points**: `student_registration/static/css/redesign.css` and `student_registration/static/js/mscc/mscc.js`.
*   **Base templates**: `student_registration/templates/base.html` (global shell), `templates/_sidebar_links.html` (navigation), `templates/mscc/base.html` (module shell reused by ALP), `templates/django_tables2/bootstrap5.html` (table rendering).
*   **Registration wizard (`mscc.js`)**: client-side validation using Bootstrap 5 states (`.is-invalid`), plus the AJAX duplicate check, avoiding server round-trips for basic errors.
*   **Data visualization**: **D3.js** for the Wellbeing Analysis dashboard (`wellbeing_dashboard.js`) and the attendance heatmaps.
*   **Mapping**: **Leaflet.js** for center and school maps, fed by the `centers_geo_data` and `alp:school_geo_data` JSON endpoints.
*   **Notifications**: **Firebase Cloud Messaging**. `static/firebase-messaging-sw.js` is the service worker; `static/js/firebase-messaging.js` registers the browser token against `save_fcm_token`.
*   **Node tooling**: `package.json` still pins a legacy gulp 3 pipeline. It is not required to run or build the application — static assets are committed and served directly.

---

## 7. Background Processing (Celery)

Long-running operations, specifically data exports, must not block the main WSGI server.

```
CELERY_TASK_QUEUES  = default, mscc_export
CELERY_TASK_ROUTES  = student_registration.mscc.tasks.generate_mscc_export → mscc_export
CELERY_RESULT_BACKEND = django-db
```

### Export workflow
1.  **Request**: user triggers an export in the UI (standard reports, or the advanced exporter).
2.  **Task enqueue**: a Celery task in `student_registration/mscc/tasks.py` is dispatched to the `mscc_export` queue.
3.  **Processing**: the worker iterates over optimized database views (`vw_mscc_child`, `vw_mscc_data`, `mscc_followupservice`), writing chunks into CSV/XLSX files inside a ZIP, persisted through the `ExportStorage` model.
4.  **Completion**: on success or failure the worker calls `send_push_to_web`, which delivers an FCM message to the requesting user's browser.
5.  **Retrieval**: the user downloads the generated file from the export list.

Run the dedicated worker with limited concurrency so a heavy export cannot starve the default queue:

```bash
celery -A student_registration.taskapp worker -Q mscc_export --concurrency=1 -l info
```

### Push notification credentials

`student_registration/backends/utils.py` initialises `firebase-admin` from a **service-account JSON file at `utility/firebase-creds.json`**. The legacy `FCM_SERVER_KEY` environment variable is no longer read anywhere in the codebase — do not rely on it. The browser-side Firebase web config is currently hardcoded in `static/js/firebase-messaging.js` and `static/firebase-messaging-sw.js`.

> **Security note:** a real service-account key is currently committed at `utility/firebase-creds.json`, and `config/settings/base.py` still carries a hardcoded `DATABASE_URL` default containing credentials. Both should be moved to environment configuration and the credentials rotated.

---

## 8. In-App Documentation

The documentation in this repository is served to users from inside the application by `student_registration/dashboard/views.py`:

| Route | Source | Access |
|---|---|---|
| `/dashboard/wiki/<page>/` | `docs/wiki/<page>.md`, rendered with `markdown` and sanitized with `bleach` | Any authenticated user |
| `/dashboard/guide/<page>/` | `docs/wiki_html/<page>.html`, inner `<div id="content">` extracted and sanitized | Superusers only — except `end_user`, which every authenticated user may read |

The list of guide pages is `WIKI_HTML_PAGES` in the same module. If you add a page to `docs/wiki_html/`, add it there too, and add the matching Markdown source under `docs/wiki/`.

`docs/wiki_html/` is generated from `docs/wiki/` — run:

```bash
python docs/build_wiki_html.py
```

after editing any Markdown page so the two stay in sync. The numbered developer pages (`01_project_overview` … `13_testing`) are hand-maintained HTML and are left untouched by the generator.

---

## 9. Testing & Development Guidelines

### Setup (Docker-based)
1.  Copy `env.example` to `.env` and fill in at least `DATABASE_URL` and `DJANGO_SECRET_KEY`.
2.  Start the stack: `docker compose -f local.yml up --build`.
3.  Run migrations: `docker compose -f local.yml exec django python manage.py migrate`.
4.  Create superuser: `docker compose -f local.yml exec django python manage.py createsuperuser`.

### Testing
*   Test settings live in `config/settings/test.py`; `pytest.ini` sets `DJANGO_SETTINGS_MODULE=config.settings.test`.
*   Run the suite with `pytest`, or a subset with `pytest student_registration/alp/tests`.
*   `coverage run manage.py test` + `coverage html` produces an HTML coverage report.
*   Test dependencies (`pytest-django`, `factory-boy`, `django-test-plus`, `coverage`, `flake8`) live in `requirements/test.txt`.
*   A PostgreSQL database is required — the models use PostgreSQL-only fields.
*   The ALP module has the densest test coverage in the tree (`student_registration/alp/tests/`) and is a good template for new tests.

### Contributing
*   Prefer modular JavaScript over monolithic jQuery files.
*   Apply the appropriate group check and queryset scoping to **every** new view or API endpoint, and update `docs/ACCESS_CONTROL.md`.
*   Follow PEP8; `setup.cfg` configures `flake8`/`pycodestyle` with a 120-character line limit.
*   Do not commit compiled translation binaries (`*.mo`) — they are gitignored deliberately. Run `./manage.py compilemessages` at deploy time.
*   Update the documentation under `docs/` in the same change as the feature; it is user-visible inside the app.
