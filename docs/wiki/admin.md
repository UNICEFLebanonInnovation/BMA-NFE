# System Administration Guide: Student Registration Compiler

This guide provides instructions for deploying, configuring, monitoring, and maintaining the **Student Registration Compiler**. It is intended for IT operations teams and system administrators.

---

## 1. System Deployment Overview

The platform uses Docker and Docker Compose to containerize its components, ensuring consistent deployments across environments.

*   **Django Application (`gunicorn`)**: The main web server handling HTTP requests and application logic.
*   **PostgreSQL (`postgres`)**: The primary relational database for persistent data storage.
*   **Redis (`redis`)**: The in-memory data store acting as a cache backend and Celery message broker.
*   **Celery Workers & Beat (`celery`, `celerybeat`)**: Background processes for asynchronous tasks (e.g., data exports, scheduled jobs).
*   **Nginx (`nginx`)**: The reverse proxy and load balancer in production, serving static/media files.
*   **Certbot**: Handles automated SSL/TLS certificate issuance and renewal.

**Deployment Reference**:
*   Detailed setup instructions can be found in `docs/deployment.md` and `docs/ministry_handover.md`.
*   The `.env` file must be securely configured with `DATABASE_URL`, `DJANGO_SECRET_KEY`, `FCM_SERVER_KEY`, and Sentry DSN.

---

## 2. Role-Based Access Control (RBAC)

The system enforces strict data isolation based on user roles and associations.

### Core Roles
1.  **MSCC_CENTER (Center Staff)**: Can view and manage data *only* for their assigned center.
2.  **MSCC_PARTNER (Partner Organization Staff)**: Has view-only access across all centers associated with their partner organization. They cannot add or edit records.
3.  **Administrators (Superusers)**: Full system access across all centers and partners.

### Enforcement Mechanisms
*   **Backend Isolation**: Implemented via Django view mixins (`MSCCAccessMixin`) and view decorators (`mscc_access_required`).
*   **Template Filtering**: UI components hide unauthorized actions (e.g., "Add New Student" buttons are hidden from `MSCC_PARTNER` users).

Administrators must configure user accounts via the **Django Admin Panel**, assigning the correct `Group` and associating the user with a specific `Center` or `Partner` instance.

---

## 3. Managing Background Tasks (Celery)

The platform leverages Celery to offload resource-intensive operations, primarily data exports.

*   **Dedicated Queues**: Long-running MSCC exports are routed to the `mscc_export` queue to prevent blocking smaller, frequent tasks.
*   **Concurrency**: By default, the `mscc_export` worker is configured with limited concurrency (`--concurrency=1`) to manage server load during massive CSV/XLSX generation.
*   **Monitoring**: Use the Django Admin interface under "Periodic tasks" (`django-celery-beat`) to schedule recurring jobs and view execution histories.

**Common Maintenance Tasks**:
*   To check Celery worker status: `docker compose -f production.yml logs -f celery`
*   To start a dedicated export worker: `celery -A student_registration.taskapp worker -Q mscc_export --concurrency=1 -l info`

---

## 4. Notifications & Firebase (FCM)

When background tasks (like exports) complete, the system notifies the requesting user in real-time via **Firebase Cloud Messaging**.

*   **Configuration**: The `FCM_SERVER_KEY` must be set in the `.env` file.
*   **Frontend Integration**: The client uses a Service Worker (`firebase-messaging-sw.js`) to listen for incoming push events.
*   **Export Notification Flow**: Once Celery finishes building a ZIP/CSV file, it triggers a push message. The frontend displays a "Download Ready" modal, allowing the user to retrieve the file immediately.

---

## 5. Routine Operations & Disaster Recovery

### Routine Maintenance
1.  **Database Migrations**: Run after code updates.
    *   `docker compose -f production.yml exec django python manage.py migrate`
2.  **Static Files**: Collect static assets after UI changes.
    *   `docker compose -f production.yml exec django python manage.py collectstatic --noinput`

### Backups
*   **Automated Backups**: Schedule `pg_dump` via cron.
    *   `docker compose -f production.yml exec postgres pg_dump -U $POSTGRES_USER -F c -f /backups/student_$(date +%F).dump $POSTGRES_DB`
*   **Media Files**: Ensure the `/media/` volume is backed up, as it contains user uploads and generated export files.

### Restoration
*   To restore a database dump:
    *   `docker compose -f production.yml exec postgres pg_restore -U $POSTGRES_USER -d $POSTGRES_DB /path/to/dump`

---

## 6. System Monitoring & Error Logging

*   **Sentry**: The application integrates with Sentry for real-time error tracking. Ensure the `DJANGO_SENTRY_DSN` is set in the `.env` file. Sentry automatically captures unhandled exceptions (e.g., HTTP 500s) and detailed stack traces.
*   **Log Files**: Docker service logs provide the primary insight into system health.
    *   `docker compose -f production.yml logs -f django`
    *   `docker compose -f production.yml logs -f nginx`