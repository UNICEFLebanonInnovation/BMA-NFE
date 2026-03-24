# Developer Guide: Student Registration Compiler

Welcome to the **Developer Guide**. This document details the technical architecture, core Django applications, and the frontend ecosystem, providing context for maintaining and extending the platform.

---

## 1. Codebase Architecture Overview

The system is a monolithic Django application designed for high operational data throughput.

*   **Django Backend (`student_registration/`)**: The core application logic, relying on PostgreSQL for persistence and Redis for caching/brokering.
*   **Frontend Redesign**: Modernized with Bootstrap 5.3 and Vanilla JS. It utilizes a custom theme based on UNICEF guidelines.
*   **Asynchronous Processing**: Celery handles background exports, and `django-celery-beat` manages periodic scheduling.
*   **Tooling**: Managed via `manage.py`, configured using environment variables (`.env`), and deployed via Docker Compose.

---

## 2. Core Django Apps

The codebase is organized into domain-specific applications:

1.  **`users/` & `accounts/`**:
    *   **Responsibilities**: Authentication, RBAC (Role-Based Access Control), profile management.
    *   **Key Components**: Custom User models, `MSCCAccessMixin` for CBVs, and `mscc_access_required` decorators for FBVs.
2.  **`students/` & `mscc/`**:
    *   **Responsibilities**: The core Non-Formal Education (NFE) logic.
    *   **Key Components**: Registration workflows (multi-step wizard), `Teacher` models, `School` records, and related services (PSS, Education).
    *   **Background Jobs**: `mscc.tasks` contains Celery tasks for heavy CSV/XLSX generation.
3.  **`attendances/`**:
    *   **Responsibilities**: Tracking student presence.
    *   **Key Components**: Bulk attendance entry, heatmaps, and absence logging.
4.  **`locations/` & `schools/`**:
    *   **Responsibilities**: Reference data for physical sites and infrastructure.
    *   **Key Components**: Autocomplete views, maps, and geolocation data.
5.  **`taskapp/`**:
    *   **Responsibilities**: Centralized configuration and autodiscovery for Celery tasks.

---

## 3. Database Schema & PostgreSQL Optimizations

The system leverages PostgreSQL-specific features heavily, meaning **SQLite is not supported for development or testing**.

### Key Optimizations
*   **ArrayField & JSONField**: Used extensively in `Registration`, `Assessment`, and `School` models to handle variable data structures without excessive join tables.
*   **Analytics Indexing**: Complex queries (like the Wellbeing Dashboard) rely on specific indexes (`CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_mscc_registration_created`).
*   **Aggregations**: Use Django's `NullIf` to safely handle potential division-by-zero errors when calculating educational improvements.
*   **Age Bucketing**: Advanced ORM usage (`Case/When` + `ExtractYear(Now())`) groups beneficiaries into analytical cohorts dynamically.

---

## 4. Frontend Ecosystem (Redesign)

The platform was recently modernized from an older jQuery/ArchitectUI stack to a lighter, more performant Bootstrap 5 architecture.

### Key Implementation Patterns
*   **Entry Points**: `student_registration/static/css/redesign.css` and `student_registration/static/js/mscc/mscc.js`.
*   **Layout Engine**: Flexbox-based sidebar and main content areas (`base.html`), eliminating nested structural complexity.
*   **Registration Wizard (`mscc.js`)**: Implements client-side validation using Bootstrap 5 states (`.has-error`, `.is-invalid`), preventing server roundtrips for basic errors.
*   **Data Visualization**: Uses **D3.js** for the "Wellbeing Analysis" dashboard (`wellbeing_dashboard.js`) and attendance heatmaps.
*   **Mapping**: Uses **Leaflet.js** for interactive center/school geographic mapping, fed by a JSON API endpoint.
*   **Notifications**: Uses **Firebase Cloud Messaging (FCM)**. The `firebase-messaging-sw.js` service worker handles background pushes, displaying an "Export Ready" modal when Celery tasks complete.

---

## 5. Background Processing (Celery)

Long-running operations, specifically data exports, must not block the main WSGI server.

### Export Workflow
1.  **Request**: User triggers an export in the UI (e.g., standard reports, or pivot data).
2.  **Task Enqueue**: A Celery task (`student_registration/mscc/tasks.py`) is dispatched to the `mscc_export` queue.
3.  **Processing**: The worker iterates over optimized database views (`vw_mscc_child`, etc.), writing chunks to a CSV/XLSX file within an `ExportStorage` model.
4.  **Completion**: Upon success (or failure), the worker fires an FCM push notification to the user's browser.
5.  **Retrieval**: The user clicks the notification to download the generated file from the `/media/` directory.

---

## 6. Testing & Development Guidelines

### Setup (Docker-based)
1.  Copy `env.example` to `.env`.
2.  Start the stack: `docker compose -f local.yml up --build`.
3.  Run migrations: `docker compose -f local.yml exec django python manage.py migrate`.
4.  Create superuser: `docker compose -f local.yml exec django python manage.py createsuperuser`.

### Testing
*   **Unit/Integration Tests**: The system uses `pytest`. Run tests via `pytest.ini` or `coverage run manage.py test`.
*   **Frontend End-to-End (E2E)**: The registration flow is verified using **Playwright**.
    *   Ensure Chromium dependencies are installed: `playwright install chromium --with-deps`.
    *   Target local login endpoints (`/accounts/login/`) accurately.

### Contributing
*   Prioritize modular JavaScript over monolithic jQuery files.
*   Ensure RBAC checks (`mscc_access_required`) are applied to any new API endpoints or views.
*   Follow PEP8 guidelines for Python code and run `flake8` or `black` before committing.