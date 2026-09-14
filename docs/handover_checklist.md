# Ministry Handover Checklist

**Revision: September 2026**

Use this checklist to verify the platform is production-ready and clearly owned by the Ministry team before the handover.

## Environment and access
- [ ] Production `.env` file completed with real secrets: `DATABASE_URL`, `DJANGO_SECRET_KEY`, `DJANGO_ALLOWED_HOSTS`, `DJANGO_CSRF_TRUSTED_ORIGINS`, `DJANGO_ADMIN_URL`, email settings and `DJANGO_SENTRY_DSN`.
- [ ] `DATABASE_URL` set explicitly — the hardcoded fallback in `config/settings/base.py` is **not** in use, and the credentials it contains have been rotated.
- [ ] Firebase service-account key rotated and supplied outside version control (the copy committed at `utility/firebase-creds.json` has been invalidated).
- [ ] The `DJANGO_SECRET_KEY` committed in `dev.env` is not used in any live environment.
- [ ] Administrative access to DNS records confirmed and domain updated to point at the production host.
- [ ] At least two Ministry administrators have SSH access to the server and permissions to run Docker.
- [ ] Repository cloned on the production host; `.env` stored securely with restricted permissions.

## Deployment validation
- [ ] `docker compose -f production.yml up --build -d` completes without errors.
- [ ] Database migrations executed: `docker compose -f production.yml exec django python manage.py migrate`.
- [ ] Static assets collected: `docker compose -f production.yml exec django python manage.py collectstatic --noinput`.
- [ ] Translations compiled: `docker compose -f production.yml exec django python manage.py compilemessages` (`.mo` files are not committed).
- [ ] Superuser created for Ministry operations: `docker compose -f production.yml exec django python manage.py createsuperuser`.
- [ ] Site reachable over HTTPS at the public domain; admin interface reachable at `<domain>/<DJANGO_ADMIN_URL>`.

## Services and monitoring
- [ ] Celery worker and beat containers running; `mscc_export` queue tested with a sample export.
- [ ] Certbot certificates issued or renewed successfully; expiry dates recorded.
- [ ] Sentry DSN configured and a test error captured to confirm alerts.
- [ ] Email delivery verified with a password reset or invitation email.
- [ ] Firebase push notifications tested with a sample export completion (using the service-account file, not `FCM_SERVER_KEY`).
- [ ] Role setup verified: at least one working account per module in use (`MSCC_CENTER`, `MSCC_PARTNER`, `ALP_SCHOOL`, CLM roles), each with its center/partner/school assigned.
- [ ] ALP school accounts confirmed to see only their own school's data.

## Data protection and backups
- [ ] Automated PostgreSQL backups scheduled (e.g., cron invoking `pg_dump` via Docker Compose) with offsite storage.
- [ ] Restore process tested using `pg_restore` against a staging database.
- [ ] `media/` directory synchronized to durable storage and included in backups.
- [ ] `.env` and encryption keys stored securely according to Ministry policy.

## Operations and documentation
- [ ] Ministry team has reviewed the [Ministry Handover Guide](./ministry_handover.md) and knows start/stop, upgrade, and recovery steps.
- [ ] In-app documentation reachable and current: End User Manual at `/dashboard/guide/end_user/`, technical guides for superusers, and `python docs/build_wiki_html.py` run after the last documentation change.
- [ ] Runbook for incidents (log locations, restart commands, escalation contacts) documented internally.
- [ ] Ownership documented: primary product owner, technical owner, and on-call rotation.
- [ ] Support channels established (email/phone/chat) and response times agreed.

Completing this checklist ensures the Ministry receives a fully operable system with clear ownership and recovery procedures.
