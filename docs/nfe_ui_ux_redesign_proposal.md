# BMA NFE Sector UI/UX Redesign Proposal

This document captures the target IA, wireframe layout guidance, and implementation sequence for the BMA NFE UI redesign. It is intended as the product + engineering handoff baseline.

## Information Architecture

### Primary Modules
- Dashboard (landing page with overview + quick actions)
- Registration (guided wizard for new beneficiaries)
- Beneficiaries (search + profile management)
- Operations
  - Attendance
  - Centers & Schools
  - Teachers
- Analytics & Reporting
  - Standard Reports
  - Pivot Builder
  - Insights
- Admin
  - Roles and permissions
  - Reference data (Governorates/Cazas/etc.)
  - Audit logs

### Registration Flow
1. Dashboard -> Quick Action: Register New
2. Identity (with duplicate checks)
3. Caregiver Info
4. Vulnerability / Education Status
5. Review and confirmation
6. Success screen with print/register-another actions

## Key Screen Patterns

### Login
- Minimal centered card
- Username/email + password with toggle visibility
- Remember me + forgotten password
- Inline validation errors under fields

### Dashboard
- Metrics row (active students, attendance rate, pending exports)
- Quick action tiles
- Recent activity feed + my tasks

### Registration Wizard
- Horizontal stepper
- Two-column body layout
- Context sidebar for potential duplicates
- Sticky footer actions: Back / Save Draft / Next

### Beneficiary Profile
- Header summary (photo, status, primary phone)
- Tabs: Overview, Enrollment, Attendance, Services
- Actions: Edit, Deactivate, Transfer, Print ID

### Case / Enrollment Tracking
- Full-width table + quick filter chips
- Status badges + priority flags + last interaction date
- Global search by ID/name/caregiver phone

### Insights
- KPI summary cards + chart widgets
- Dashboard-level filter by center/date range
- Export actions visible on each widget

### Admin
- Left sub-navigation by settings category
- Role permission matrix
- Searchable audit log

## Design System Baseline

### Typography
- Font family: Inter
- H1 32px Bold
- H2 24px Semibold
- Body 16px Regular
- Caption 13px Medium

### Spacing and Grid
- 8px base spacing
- 24px desktop margins, 16px mobile margins
- 1440px max content width

### Components (Bootstrap 5.3)
- Buttons:
  - Primary: UNICEF blue `#0097D7`
  - Secondary: outline variants
  - Danger: `#D93025`
- Forms:
  - Top labels
  - 48px input height
  - Inline validation feedback
- Tables:
  - Sticky headers
  - Zebra striping
  - Row kebab menu for secondary actions
- Navigation:
  - Topbar (logo/search/profile)
  - Collapsible sidebar (240px -> icon state)

## UX Enhancements

- Bulk actions with selection bar
- Non-blocking duplicate detection alerts
- Offline draft persistence (localStorage)
- Record-level audit trail panel (who/what/when)

## Implementation Sequence

1. Add `templates/base_redesign.html` shell using Bootstrap 5.3 and a sidebar/main Flexbox layout.
2. Enable RTL via `dir` support and Bootstrap RTL assets.
3. Migrate reusable card wrappers to Bootstrap 5 `.card`.
4. Replace smartwizard pages with native stepper components.
5. Modularize form logic currently in `mscc.js` into smaller UI controllers.
6. Standardize iconography with Lucide SVG icons.

## Suggested Rollout

1. Build a clickable prototype for registration flow.
2. Run 5-10 usability sessions with field operators.
3. Release in phases (new dashboard/navigation first, legacy forms temporarily retained).
