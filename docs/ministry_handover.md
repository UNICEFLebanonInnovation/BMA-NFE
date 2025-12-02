# Ministry Handover Guide

This document explains how to run, operate, and support the Student Registration Compiler when it is handed over to a Ministry IT operations team. It focuses on explicit, actionable steps so that administrators can deploy, monitor, and troubleshoot the platform without prior project context.

## 1. System overview
- **Application**: Django 4.x project located in the `student_registration/` folder with multiple domain apps (accounts, students, attendances, mscc, clm, schools).
- **Database**: PostgreSQL 12+ stores all persistent data (users, students, attendance records, schedules, Celery beat metadata).
- **Cache/Broker**: Redis is used as the Celery broker and for Django caching.
- **Background jobs**: Celery workers process exports and asynchronous tasks; Celery beat schedules recurring jobs.
- **Web server**: Gunicorn serves the Django WSGI app; Nginx proxies requests and serves static files in production.
- **Containers**: `local.yml` (development) and `production.yml` (production) define the complete Docker Compose stacks.
- **Source control**: Keep this repository together with the `.env` file used in production for disaster recovery and redeployment.

## 2. Prerequisites
- **Host machine**: Linux server with Docker and Docker Compose v2 installed, 4 CPU cores, and 8 GB RAM minimum.
- **Network**: Public DNS record pointing to the host. Ports 80/443 must be reachable for HTTP/HTTPS and Let’s Encrypt certificate issuance.
- **Storage**: Allocate disk space for database backups and `static/`/`media/` assets (recommend 50 GB to start).
- **Accounts**: Non-root Linux user with permission to run Docker, and access to project repository.

## 3. Environment configuration
All required environment variables live in an `.env` file. Start from `env.example` and fill in production values before running the stack.

### Core settings
- `DJANGO_SECRET_KEY`: Long random string; keep private.
- `DJANGO_ALLOWED_HOSTS`: Comma-separated list of hostnames (e.g., `portal.gov.lb,www.portal.gov.lb`).
- `DJANGO_SETTINGS_MODULE`: Use `config.settings.production` for production deployments.
- `DJANGO_ADMIN_URL`: URL path segment for the admin (e.g., `admin/`).
- `DJANGO_SECURE_SSL_REDIRECT`: Set to `True` when HTTPS is enabled.

### Database and cache
- `POSTGRES_USER` / `POSTGRES_PASSWORD`: PostgreSQL credentials (also referenced by Docker Compose). Use strong passwords.
- `POSTGRES_DB`: Optional custom database name; defaults to the service name if unset.
- `REDIS_URL` (if needed): Override to point to external Redis if not using the bundled container.

### Email and notifications
- `DJANGO_SERVER_EMAIL`, `DJANGO_MAILGUN_API_KEY`, `MAILGUN_SENDER_DOMAIN`: Outbound email configuration.
- `FCM_SERVER_KEY`: Firebase Cloud Messaging server key for push notifications.
- `FIREBASE_*` variables: Client configuration values for frontend Firebase initialization (API key, auth domain, project ID, storage bucket, messaging sender ID, app ID, measurement ID).

### Monitoring and logging
- `DJANGO_SENTRY_DSN`: Sentry DSN for error reporting (optional but recommended).
- `COMPRESS_ENABLED`: Set to `True` to enable Django Compressor in production.

Store the final `.env` file alongside the production server. Backup this file securely because it is required for redeployment.

## 4. Deployment steps (production)
1. **Copy code and environment file**
   - Clone the repository to the server and place the `.env` file in the repository root.
2. **Build and start services**
   - Run `docker compose -f production.yml up --build -d` from the repository root. This starts PostgreSQL, Redis, Gunicorn-backed Django, Nginx, Celery worker, and Celery beat.
3. **Run migrations and collect static files**
   - `docker compose -f production.yml exec django python manage.py migrate`
   - `docker compose -f production.yml exec django python manage.py collectstatic --noinput`
4. **Create an admin account** (once per environment)
   - `docker compose -f production.yml exec django python manage.py createsuperuser`
5. **Verify health**
   - Open `https://<your-domain>/` to confirm the site loads.
   - Check `https://<your-domain>/<DJANGO_ADMIN_URL>` for admin access.
   - Review logs with `docker compose -f production.yml logs -f nginx django celeryworker celerybeat`.

## 5. Routine operations (runbook)
- **Start/stop services**: `docker compose -f production.yml up -d` to start; `docker compose -f production.yml down` to stop.
- **Apply database migrations after code updates**: `docker compose -f production.yml exec django python manage.py migrate`.
- **Rotate static files after UI changes**: `docker compose -f production.yml exec django python manage.py collectstatic --noinput`.
- **Celery queues**: Long-running exports use the `mscc_export` queue. Run an extra worker if needed:
  - `docker compose -f production.yml exec django celery -A student_registration.taskapp worker -Q mscc_export --concurrency=1 -l info`
- **Log locations**:
  - Docker service logs: `docker compose -f production.yml logs -f <service>`
  - Application logs (inside container): `/app/logs/` if configured; otherwise Docker stdout.
- **Database backups** (example cron-friendly command):
  - `docker compose -f production.yml exec postgres pg_dump -U $POSTGRES_USER -F c -f /backups/student_registration_$(date +%F).dump $POSTGRES_DB`
  - Ensure `/backups` on the host is persisted and included in your backup policy.
- **Restoring backups**:
  - Copy the dump file into the container and run `pg_restore -U $POSTGRES_USER -d $POSTGRES_DB /path/to/dump`.
- **SSL certificates**: Certbot inside `production.yml` auto-requests certificates. Update domain/email in `production.yml` before the first run and renew via the scheduled Certbot container.

## 6. Administrative usage
- **User management**: Admins can add/edit users, reset passwords, and assign roles from the Django admin interface.
- **School and student data**: Manage schools, students, attendance records, and MSCC workflows through their respective admin sections and UI flows.
- **Rate limiting and security**: Middleware enforces session limits and lockout protection. Keep `DJANGO_SECURE_SSL_REDIRECT=True` and serve behind HTTPS.

## 7. Update procedure
1. Pull the latest code from the repository branch intended for production.
2. Rebuild and restart services: `docker compose -f production.yml up --build -d`.
3. Apply migrations and collect static files (see section 4).
4. Verify critical flows (login, student search, export) after the deployment.

## 8. Disaster recovery
- Keep copies of the `.env` file, database backups, and the production `media/` folder in an offsite secure location.
- To redeploy on a new host: install Docker/Compose, clone the repository, place the `.env` file, restore the database dump, sync the `media/` directory, and start the stack using the deployment steps.

## 9. Support contacts and ownership
- Record the primary Ministry team contact, escalation chain, and vendor/support partner in an internal document stored with this repository.
- Ensure at least two administrators have access to the server and DNS records.

By following this guide, the Ministry IT team can operate the platform independently with minimal external assistance.
