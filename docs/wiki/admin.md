# System Administration Guide: BMA — NFE Sector Platform

**Revision: September 2026**

This guide provides instructions for deploying, configuring, monitoring, and maintaining the platform. It is intended for IT operations teams and system administrators.

---

## 1. System Deployment Overview

The platform uses Docker and Docker Compose to containerize its components, ensuring consistent deployments across environments.

| Service | Role |
|---|---|
| `django` (Gunicorn) | Main web server handling HTTP requests and application logic |
| `postgres` | Primary relational database for persistent data |
| `redis` | Cache backend and Celery message broker |
| `celery` / `celerybeat` | Background workers and the periodic-task scheduler |
| `nginx` | Reverse proxy, serving static and media files in production |
| `certbot` | Automated SSL/TLS certificate issuance and renewal |

**Deployment reference**

*   Step-by-step instructions: [`docs/deployment.md`](../deployment.md) and [`docs/ministry_handover.md`](../ministry_handover.md).
*   Go-live verification: [`docs/handover_checklist.md`](../handover_checklist.md).
*   The `.env` file must be configured with at least `DATABASE_URL`, `DJANGO_SECRET_KEY`, `DJANGO_ALLOWED_HOSTS`, `DJANGO_SETTINGS_MODULE=config.settings.production`, and `DJANGO_SENTRY_DSN`.

> **Do not rely on the built-in defaults.** `config/settings/base.py` still ships a hardcoded `DATABASE_URL` default containing credentials. Always set `DATABASE_URL` explicitly in `.env`, and treat the committed default as a credential that needs rotating.

---

## 2. Role-Based Access Control (RBAC)

The system enforces data isolation based on group membership combined with the center, partner or school linked to the user account.

### Groups in use

| Group | Scope |
|---|---|
| `MSCC` | Standard MSCC module access — registrations, services, assessments, grading, attendance |
| `MSCC_CENTER` | Same as `MSCC`, but lists are filtered to the user's assigned center |
| `MSCC_PARTNER` | View-oriented access across the centers of the user's partner organization; cannot add or edit registrations |
| `MSCC_FULL` | Bypasses the center/partner filter on the MSCC registration list |
| `MSCC_UNICEF` | Broad analytical and reporting visibility for UNICEF staff |
| `YOUTH` | Youth-stream users; surfaced as a distinct user type in the Django admin filters |
| `ALP_SCHOOL` | ALP school focal points. Required for every `/alp/` view; data is scoped to the user's school |
| `CLM_Bridging` | Core CLM bridging workflows — assessments, services, clubs, meetings, health visits, follow-ups |
| `CLM_BRIDGING_ALL` | Cross-cutting CLM access plus CLM export capabilities |
| `CLM_ATTENDANCE` | CLM attendance entry only |
| `CLM_TEACHER` | CLM teacher profile management |
| `CLM_Inclusion` | CLM inclusion workflows |
| `EXPORT` | Unlocks export actions on lists that gate them |

The authoritative role → view matrix lives in [`docs/ACCESS_CONTROL.md`](../ACCESS_CONTROL.md).

### Enforcement mechanisms

*   **Backend:** `GroupRequiredMixin` (`group_required`) on class-based views and the `has_group()` helper in views and templates.
*   **Queryset scoping:** views filter by the user's `center`, `partner` or `school`. ALP centralizes this in `alp/utils.filter_by_school()`.
*   **Template filtering:** UI components hide unauthorized actions (for example, "Add New Student" is hidden from `MSCC_PARTNER` users).

### Two ALP specifics worth knowing

1.  An `ALP_SCHOOL` user with **no school assigned** sees empty lists everywhere — assigning the school on the user record is part of account setup, not optional.
2.  **Superusers are intentionally read-only in ALP.** `ALPEditPermissionMixin` denies add/edit/delete to superusers so school-owned data is only entered by the school. A superuser also needs the `ALP_SCHOOL` group to open ALP pages at all.

Administrators configure accounts via the **Django Admin Panel**, assigning the correct `Group` and associating the user with a `Center`, `Partner` or `School`.

---

## 3. Application Configuration Reference

| Setting | Location | Value / behaviour |
|---|---|---|
| Auto logout | `production.py` → `AUTO_LOGOUT_DELAY` | 30 minutes of inactivity (production only) |
| Failed-login throttle | `production.py` → `ACCOUNT_RATE_LIMITS` | `login_failed: 5/5m`, `login_user: 10/m`, `signup: 3/h` |
| Password policy | `base.py` → `AUTH_PASSWORD_VALIDATORS` | Minimum 8 characters, at least 3 digits, 1 uppercase, 1 lowercase, 1 symbol, plus Django's similarity/common/numeric checks |
| Languages | `base.py` → `LANGUAGES` | Arabic and English, with RTL layout for Arabic |
| Time zone | `base.py` → `TIME_ZONE` | `Asia/Beirut` |
| Session hardening | `production.py` | `SESSION_COOKIE_SECURE`, `SESSION_COOKIE_HTTPONLY`, `CSRF_COOKIE_SECURE`, `CSRF_USE_SESSIONS`, `X_FRAME_OPTIONS=DENY`, HSTS enabled |
| Admin URL | `.env` → `DJANGO_ADMIN_URL` | Set a non-obvious path; the admin is mounted there |

Rounds, programmes and ALP grading definitions (subject, minimum grade, maximum grade) are reference data maintained through the Django admin. Adding a grading definition immediately changes the ALP grading form — no deployment is needed.

---

## 4. Managing Background Tasks (Celery)

The platform uses Celery to offload resource-intensive operations, primarily data exports.

*   **Queues:** `default` and `mscc_export`. `student_registration.mscc.tasks.generate_mscc_export` is routed to `mscc_export` so long exports cannot block smaller tasks.
*   **Concurrency:** run the `mscc_export` worker with `--concurrency=1` to bound memory use during large CSV/XLSX generation.
*   **Results:** stored in the database (`django-celery-results`); browse them in the admin under *Task results*.
*   **Schedules:** managed in the admin under *Periodic tasks* (`django-celery-beat`).

**Common maintenance commands**

```bash
# Worker status
docker compose -f production.yml logs -f celery

# Dedicated export worker
celery -A student_registration.taskapp worker -Q mscc_export --concurrency=1 -l info
```

---

## 5. Notifications & Firebase (FCM)

When a background export completes, the system notifies the requesting user in real time via **Firebase Cloud Messaging**.

*   **Server credentials:** `firebase-admin` is initialised from a service-account JSON file at `utility/firebase-creds.json`. The legacy `FCM_SERVER_KEY` environment variable is **no longer read by the application** — older documentation that told you to set it is out of date.
*   **Browser tokens:** the client registers a device token through the `save_fcm_token` endpoint; tokens are stored in the `WebPushToken` model. A user with no registered token simply receives no push (the export still completes and remains downloadable).
*   **Frontend integration:** `static/firebase-messaging-sw.js` is the service worker; the Firebase web config is currently hardcoded in `static/js/firebase-messaging.js`.
*   **Flow:** Celery finishes the export → `send_push_to_web` sends the message → the frontend shows a "Download Ready" prompt.

> **Security:** the service-account private key is currently committed to the repository. Treat it as compromised, rotate it in the Firebase console, and load it from a secret store or a mounted file outside version control.

---

## 6. Documentation Access Inside the Application

The docs in this repository are served to signed-in users:

| Route | Source | Who can read it |
|---|---|---|
| `/dashboard/guide/end_user/` | `docs/wiki_html/end_user.html` | Any authenticated user |
| `/dashboard/guide/<page>/` (all other pages) | `docs/wiki_html/*.html` | Superusers only |
| `/dashboard/wiki/<page>/` | `docs/wiki/*.md` | Any authenticated user |

Note the asymmetry: the HTML guide route restricts technical pages to superusers, but the Markdown route does **not**. If technical documentation must be superuser-only, `WikiPageView` needs the same check as `WikiGuidePageView`.

After editing any file in `docs/wiki/`, regenerate the HTML mirror so both routes agree:

```bash
python docs/build_wiki_html.py
```

---

## 7. Routine Operations & Disaster Recovery

### Routine maintenance
1.  **Database migrations** — run after code updates:
    `docker compose -f production.yml exec django python manage.py migrate`
2.  **Static files** — collect after UI changes:
    `docker compose -f production.yml exec django python manage.py collectstatic --noinput`
3.  **Translations** — compile after updating `.po` files (compiled `.mo` files are not committed):
    `docker compose -f production.yml exec django python manage.py compilemessages`

### Backups
*   **Database:** schedule `pg_dump` via cron.
    `docker compose -f production.yml exec postgres pg_dump -U $POSTGRES_USER -F c -f /backups/student_$(date +%F).dump $POSTGRES_DB`
*   **Media:** back up the `/media/` volume — it holds uploaded consent forms, teacher attachments, child photos and generated export files.

### Restoration
*   `docker compose -f production.yml exec postgres pg_restore -U $POSTGRES_USER -d $POSTGRES_DB /path/to/dump`
*   Test the restore against a staging database before you need it.

---

## 8. System Monitoring & Error Logging

*   **Sentry:** set `DJANGO_SENTRY_DSN` in `.env`. Sentry captures unhandled exceptions and stack traces.
*   **Azure Monitor / OpenTelemetry:** `azure-monitor-opentelemetry` is available; `OTEL_SERVICE_NAME` and `OTEL_RESOURCE_ATTRIBUTES` identify the deployment.
*   **Logs:** Docker service logs are the primary insight into system health.
    ```bash
    docker compose -f production.yml logs -f django
    docker compose -f production.yml logs -f nginx
    docker compose -f production.yml logs -f celery
    ```
*   **Broken links:** `BrokenLinkEmailsMiddleware` mails the addresses in `ADMINS` when a 404 is hit from an internal referrer.
