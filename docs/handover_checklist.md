# Ministry Handover Checklist

Use this checklist to verify the platform is production-ready and clearly owned by the Ministry team before the handover.

## Environment and access
- [ ] Production `.env` file completed with real secrets, database credentials, allowed hosts, email, Sentry, and Firebase values.
- [ ] Administrative access to DNS records confirmed and domain updated to point at the production host.
- [ ] At least two Ministry administrators have SSH access to the server and permissions to run Docker.
- [ ] Repository cloned on the production host; `.env` stored securely with restricted permissions.

## Deployment validation
- [ ] `docker compose -f production.yml up --build -d` completes without errors.
- [ ] Database migrations executed: `docker compose -f production.yml exec django python manage.py migrate`.
- [ ] Static assets collected: `docker compose -f production.yml exec django python manage.py collectstatic --noinput`.
- [ ] Superuser created for Ministry operations: `docker compose -f production.yml exec django python manage.py createsuperuser`.
- [ ] Site reachable over HTTPS at the public domain; admin interface reachable at `<domain>/<DJANGO_ADMIN_URL>`.

## Services and monitoring
- [ ] Celery worker and beat containers running; `mscc_export` queue tested with a sample export.
- [ ] Certbot certificates issued or renewed successfully; expiry dates recorded.
- [ ] Sentry DSN configured and a test error captured to confirm alerts.
- [ ] Email delivery verified with a password reset or invitation email.
- [ ] Firebase push notifications tested with a sample export completion.

## Data protection and backups
- [ ] Automated PostgreSQL backups scheduled (e.g., cron invoking `pg_dump` via Docker Compose) with offsite storage.
- [ ] Restore process tested using `pg_restore` against a staging database.
- [ ] `media/` directory synchronized to durable storage and included in backups.
- [ ] `.env` and encryption keys stored securely according to Ministry policy.

## Operations and documentation
- [ ] Ministry team has reviewed the [Ministry Handover Guide](./ministry_handover.md) and knows start/stop, upgrade, and recovery steps.
- [ ] Runbook for incidents (log locations, restart commands, escalation contacts) documented internally.
- [ ] Ownership documented: primary product owner, technical owner, and on-call rotation.
- [ ] Support channels established (email/phone/chat) and response times agreed.

Completing this checklist ensures the Ministry receives a fully operable system with clear ownership and recovery procedures.
