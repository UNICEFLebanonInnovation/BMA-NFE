# Deployment and Maintenance Guide

This document provides a comprehensive guide for deploying and maintaining the Student Registration Compiler. It is intended for developers and IT operations teams who are responsible for the project's lifecycle.

## 1. Environment Setup

The project uses a `.env` file to manage all environment-specific configurations. This file should be created in the root of the project and should not be committed to version control. The `env.example` file can be used as a template.

### 1.1. Database Configuration

The project is configured to use a PostgreSQL database. The connection details should be provided in the `.env` file using the `DATABASE_URL` variable. The format for this variable is:

```
DATABASE_URL=postgres://<user>:<password>@<host>:<port>/<database_name>
```

**Important:** The hardcoded database URL in `config/settings/base.py` has been removed to improve security and align with best practices. All database configurations should be managed through the `.env` file.

### 1.2. Other Configurations

The `.env` file should also contain other sensitive information, such as the `DJANGO_SECRET_KEY`, email server settings, and any other environment-specific variables. Refer to `env.example` for a complete list of required variables.

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
