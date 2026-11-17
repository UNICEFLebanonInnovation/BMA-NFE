# BMA — NFE Sector Platform: Interactive Code Wiki

**Revision: September 2026**

Welcome to the **BMA NFE Sector Platform** wiki (the codebase is historically named *Student Registration Compiler*). This knowledge base explains the system architecture, user workflows, administration tasks, and codebase details.

It is structured for three audiences:

1. **[End User Guide](end_user.md)** — operators, teachers, school focal points and field staff who use the system daily to register beneficiaries, track attendance, and record services.
2. **[Administrator Guide](admin.md)** — Ministry IT teams and system administrators responsible for deployment, role management, background exports, and monitoring.
3. **[Developer Guide](developer.md)** — engineers maintaining or extending the codebase: Django architecture, database models, frontend, and async task processing.

## Modules covered

| Module | Description |
|---|---|
| **MSCC (Makani)** | Child registration, service delivery, attendance and dashboards for Makani centers |
| **ALP** | Accelerated Learning Programme run by public schools — registrations, teachers, attendance, grading, school profile |
| **CLM** | Bridging / Community Learning programme workflows |
| **Reports & Analytics** | Cross-module dashboards, pivot tables, maps and background exports |

## Quick Navigation

*   **[End User Interface & Workflows](end_user.md)**
    *   Login, navigation and account management
    *   MSCC registration wizard and service delivery
    *   Attendance tracking and heatmaps
    *   The ALP module for schools
    *   Exports, dashboards and reports
*   **[System Administration](admin.md)**
    *   Deployment and environment configuration
    *   Role-based access control (RBAC) and the group list
    *   Background exports, Celery queues and Firebase notifications
    *   Backups, disaster recovery and monitoring
*   **[Codebase & Architecture](developer.md)**
    *   Django app structure (`mscc`, `alp`, `clm`, `child`, `attendances`, …)
    *   Frontend stack (Bootstrap 5, vanilla JS, D3.js, Leaflet)
    *   Database schema and PostgreSQL optimizations
    *   Celery task definitions, queues and the export pipeline
*   **[System Overview & Infrastructure](system_details.md)**
    *   Backend and frontend dependency snapshot
    *   Django applications and their models
    *   Deployment and Docker configuration
    *   Environment variables

## Related documents in the repository

| Document | Purpose |
|---|---|
| [`docs/ACCESS_CONTROL.md`](../ACCESS_CONTROL.md) | Role → view permission matrix |
| [`docs/project_overview.md`](../project_overview.md) | Repository layout and local setup |
| [`docs/deployment.md`](../deployment.md) | Deployment and maintenance guide |
| [`docs/ministry_handover.md`](../ministry_handover.md) | Ministry operations runbook |
| [`docs/handover_checklist.md`](../handover_checklist.md) | Go-live checklist |
| [`docs/developer_handover.md`](../developer_handover.md) | Concise orientation for new maintainers |
| [`docs/analytics_dashboard.md`](../analytics_dashboard.md) | Analytics API design and recommended indexes |
| [`docs/ui_ux_redesign_proposal.md`](../ui_ux_redesign_proposal.md) | UI/UX redesign rationale |
| [`DOCS_REDESIGN.md`](../../DOCS_REDESIGN.md) | Implemented design system specification |

---
*Maintained for the BMA NFE Sector system. Markdown under `docs/wiki/` is the source of truth; run `python docs/build_wiki_html.py` to refresh the HTML mirror in `docs/wiki_html/`.*
