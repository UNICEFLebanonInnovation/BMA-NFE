# Deployment and Maintenance Guide

This document provides a comprehensive guide for deploying and maintaining the Student Registration Compiler. It is intended for developers and IT operations teams who are responsible for the project's lifecycle.

## 1. Environment Setup

The project uses a `.env` file to manage all environment-specific configurations. This file should be created in the root of the project and should not be committed to version control. The `env.example` file can be used as a template.

### 1.1. Database Configuration

The project is configured to use a PostgreSQL database. The connection details should be provided in the `.env` file using the `DATABASE_URL` variable. The format for this variable is:

```
DATABASE_URL=postgres://<user>:<password>@<host>:<port>/<database_name>
```

**Important:** `DATABASE_URL` is **required**. The hardcoded fallback connection string that used to live in `config/settings/base.py` has been removed, and `env.db('DATABASE_URL')` is now called without a default, so Django will refuse to start if the variable is not set. Any environment that previously relied on the fallback must set `DATABASE_URL` explicitly. The credentials that were embedded in that fallback are considered compromised (they were committed to git history) and must be rotated on the database server.

### 1.2. Firebase Credentials

Push notifications use `firebase-admin` with a Google service-account JSON file. That file contains a private key and is **not** in version control (`utility/firebase-creds.json` is listed in `.gitignore`).

Provide it at deploy time, either by mounting the file into the container or by writing it out from a secret store, then point the application at it:

```
FIREBASE_CREDENTIALS_FILE=/run/secrets/firebase-creds.json
```

If `FIREBASE_CREDENTIALS_FILE` is unset, the application falls back to the conventional location `utility/firebase-creds.json`. When the file is missing or unreadable, push notifications are skipped and a warning is logged; nothing else in the application fails.

A service-account key for project `leb-bma` was previously committed to this repository. It must be revoked in the Firebase console and replaced with a freshly issued key.

### 1.3. Other Configurations

The `.env` file should also contain other sensitive information, such as the `DJANGO_SECRET_KEY`, email server settings, and any other environment-specific variables. Refer to `env.example` for a complete list of required variables.

**Secrets must never be committed.** `dev.env` and `env.example` ship with empty placeholders only. A literal `DJANGO_SECRET_KEY` was previously committed in `dev.env`; that key must be treated as compromised and rotated in every environment where it was used.

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

By following this guide, you can ensure a smooth and secure deployment and maintenance process for the Student Registration Compiler.
