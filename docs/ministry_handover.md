# Ministry Handover Guide

**Revision: September 2026**

This document explains how to run, operate, and support the BMA NFE Sector platform (repository name:
*Student Registration Compiler*) when it is handed over to a Ministry IT operations team. It focuses on explicit, actionable steps so that administrators can deploy, monitor, and troubleshoot the platform without prior project context.

## 1. System overview
- **Application**: Django 5.2 project located in the `student_registration/` folder with multiple domain apps — `mscc` (Makani), `alp` (Accelerated Learning Programme), `clm` (bridging), plus `child`, `students`, `attendances`, `schools`, `locations`, `dashboard` and `users`.
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
For a detailed guide on setting up the environment, please refer to the `docs/deployment.md` file. This document provides comprehensive instructions on how to configure the project, including the database and other sensitive information.

## 4. Deployment steps (production)
The `docs/deployment.md` file contains a detailed, step-by-step guide for deploying the application to a production environment. Please refer to this document for the most up-to-date instructions.

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
- **User management**: Admins can add/edit users, reset passwords, and assign roles from the Django admin interface. Every account needs both a **group** (for example `MSCC_CENTER`, `ALP_SCHOOL`, `CLM_Bridging`) and the matching **center, partner or school** assignment — a user with a group but no assignment sees empty lists. See `docs/ACCESS_CONTROL.md`.
- **Reference data**: Programme rounds, programmes and ALP grading definitions (subject with minimum and maximum grade) are maintained in the Django admin. Adding a grading definition changes the ALP grading form immediately, with no deployment.
- **School and student data**: Manage schools, students, attendance records, and MSCC/ALP workflows through their respective admin sections and UI flows.
- **ALP is read-only for administrators**: superusers can review ALP data but cannot create or edit it — that is enforced in code so school-owned records stay the school's responsibility.
- **Rate limiting and security**: Production enables auto-logout after 30 minutes of inactivity and throttles failed logins (5 per 5 minutes per account). Keep `DJANGO_SECURE_SSL_REDIRECT=True` and serve behind HTTPS.

## 7. Update procedure
1. Pull the latest code from the repository branch intended for production.
2. Rebuild and restart services: `docker compose -f production.yml up --build -d`.
3. Apply migrations, compile translations, and collect static files (see section 5).
4. Verify critical flows (login, student search, export) after the deployment.

## 8. Disaster recovery
- Keep copies of the `.env` file, database backups, and the production `media/` folder in an offsite secure location.
- To redeploy on a new host: install Docker/Compose, clone the repository, place the `.env` file, restore the database dump, sync the `media/` directory, and start the stack using the deployment steps.

## 9. Support contacts and ownership
- Record the primary Ministry team contact, escalation chain, and vendor/support partner in an internal document stored with this repository.
- Ensure at least two administrators have access to the server and DNS records.

By following this guide, the Ministry IT team can operate the platform independently with minimal external assistance.
