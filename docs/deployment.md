# Deployment and Maintenance Guide

**Revision: September 2026**

This document provides a comprehensive guide for deploying and maintaining the BMA NFE Sector platform
(repository name: *Student Registration Compiler*). It is intended for developers and IT operations teams
responsible for the project's lifecycle.

## 1. Environment Setup

The project uses a `.env` file to manage all environment-specific configurations. This file should be created in the root of the project and should not be committed to version control. The `env.example` file can be used as a template.

### 1.1. Database Configuration

The project is configured to use a PostgreSQL database. The connection details should be provided in the `.env` file using the `DATABASE_URL` variable. The format for this variable is:

```
DATABASE_URL=postgres://<user>:<password>@<host>:<port>/<database_name>
```

**Important:** `DATABASE_URL` must always be set explicitly. `config/settings/base.py` still declares a
hardcoded fallback value that contains real credentials; it must not be relied on, the credentials in it
should be rotated, and the fallback should be removed from the settings module. All database configuration
belongs in the `.env` file.

### 1.2. Other Configurations

The `.env` file should also contain other sensitive information, such as the `DJANGO_SECRET_KEY`, email
server settings, and any other environment-specific variables. Refer to `env.example` for the variable list.

| Variable | Required | Notes |
|---|---|---|
| `DATABASE_URL` | Yes | Not present in `env.example`, but must be set — see 1.1 |
| `DJANGO_SETTINGS_MODULE` | Yes | `config.settings.production` in production |
| `DJANGO_SECRET_KEY` | Yes | Generate a fresh value per environment |
| `DJANGO_ALLOWED_HOSTS` | Yes | Comma-separated hostnames |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | Yes behind a proxy | Comma-separated origins including the scheme |
| `DJANGO_ADMIN_URL` | Recommended | Non-obvious path for the Django admin |
| `DJANGO_SENTRY_DSN` | Recommended | Enables error reporting |
| `CELERY_BROKER_URL` | Yes | Redis URL; defaults to `redis://localhost:6379/0` |
| `DJANGO_SECURE_SSL_REDIRECT` | Production | Keep `True` behind HTTPS |
| `FCM_SERVER_KEY`, `FIREBASE_*` | **Obsolete** | No longer read by the application; push uses the service account at `utility/firebase-creds.json` |
| `DJANGO_OPBEAT_*` | **Obsolete** | Superseded by Sentry and `OTEL_*` |

> **Secrets hygiene:** `dev.env` contains a committed `DJANGO_SECRET_KEY` and `utility/firebase-creds.json`
> contains a committed Firebase service-account private key. Neither should be used in a real deployment;
> rotate both and supply them through your secret store.

## 2. Running the Application

The application can be run using Docker Compose, which is the recommended method for both development and production environments.

### 2.1. Local Development

To run the application in a local development environment, use the `local.yml` Docker Compose file:

```
docker compose -f local.yml up --build
```

This will start the necessary services, including the Django application, PostgreSQL database, and Redis.

### 2.2. Production Deployment

For production deployments, use the `production.yml` Docker Compose file:

```
docker compose -f production.yml up --build -d
```

This will start the application in detached mode and is suitable for a production environment.

## 3. Maintenance

### 3.1. Database Migrations

After any changes to the database models, you will need to run migrations:

```
docker compose -f production.yml exec django python manage.py migrate
```

### 3.2. Static Files

To collect static files, run the following command:

```
docker compose -f production.yml exec django python manage.py collectstatic --noinput
```

### 3.3. Translations

Compiled translation catalogues (`*.mo`) are intentionally not committed. Compile them as part of the
deployment so the Arabic interface is complete:

```
docker compose -f production.yml exec django python manage.py compilemessages
```

### 3.4. Background workers

Long exports are routed to the `mscc_export` Celery queue. Run a dedicated worker with limited concurrency
so a single large export cannot starve the default queue:

```
celery -A student_registration.taskapp worker -Q mscc_export --concurrency=1 -l info
```

### 3.5. Documentation

The documentation under `docs/` is served to signed-in users inside the application. After changing any
Markdown page under `docs/wiki/`, regenerate the HTML mirror before deploying:

```
python docs/build_wiki_html.py
```

By following this guide, you can ensure a smooth and secure deployment and maintenance process for the
platform.
