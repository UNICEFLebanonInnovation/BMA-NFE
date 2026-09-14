# Advanced Analytics API (MSCC) – ORM blueprint

**Revision: September 2026**

Implemented in `student_registration/dashboard/views.py` and routed from
`student_registration/dashboard/urls.py`.

## Data assumptions
Fact model: `Registration` (`student_registration.mscc.models.Registration`) with these joins:
- `Registration.child` (gender, nationality, birthday fields)
- `Registration.partner`
- `Registration.center`
- Latest programme from `EducationService` via subquery on `registration_id`

## Filters accepted by all endpoints
- `date_from`, `date_to`
- `partner_id`, `center_id`, `programme_id`
- `nationality`, `gender`
- `age_min`, `age_max`

## Endpoints

| Endpoint | URL name | Returns |
|---|---|---|
| `GET /dashboard/api/analytics/summary/` | `dashboard:analytics_summary` | Headline totals for the current filter set |
| `GET /dashboard/api/analytics/trend/?days=30` | `dashboard:analytics_trend` | Daily registration counts |
| `GET /dashboard/api/analytics/breakdown/?dimension=gender` | `dashboard:analytics_breakdown` | Counts grouped by one registration dimension |
| `GET /dashboard/api/analytics/teacher-breakdown/?dimension=sex` | `dashboard:analytics_teacher_breakdown` | Counts grouped by one teacher dimension |
| `GET /dashboard/api/analytics/crosstab/?x=partner&y=gender` | `dashboard:analytics_crosstab` | Two-dimensional cross-tabulation |
| `GET /dashboard/api/analytics/export.csv` | `dashboard:analytics_export_csv` | Streaming CSV of the filtered rows |

The dashboard itself is at `/dashboard/advanced-analytics/`
(`dashboard:advanced_analytics`). Related views in the same app: `/dashboard/pivot-dashboard/`,
`/dashboard/chart-builder/`, `/dashboard/centers-map/` and `/dashboard/advanced-exporter/`.

Supported dimensions for `breakdown` and `crosstab` (`DIMENSION_MAP`):
`gender`, `nationality`, `partner`, `center`, `programme`, `age_group` (`age` is accepted as an alias).
An unknown dimension returns `{"error": "Invalid dimension", "valid_dimensions": [...]}` rather than a
500.

Supported dimensions for `teacher-breakdown` (`TEACHER_DIMENSION_MAP`): `sex`, `nationality`, `center`.

## Scoping

`analytics_base_queryset()` filters `Registration.objects.filter(deleted=False)`. Users who are neither
`is_superuser` nor `is_staff` are additionally restricted to their own `partner_id` and `center_id`, so
the same endpoint returns a different slice per user — which is why the cache key below includes the
user's scope.

## Age buckets in ORM
Age is derived from birth year (from child birthday fields) and bucketed:
- `0-4`, `5-11`, `12-14`, `15-17`, `18+`
- null/invalid DOB values are mapped to `Unknown`

Implementation uses:
- `Case/When` + `Cast` to integer birth year
- `ExtractYear(Now()) - birth_year`
- second `Case` for final bucket labels

## Performance choices
- Date filtering uses `created__gte/lte` datetime bounds (index-friendly), not `created__date`
- Trend query uses `TruncDate(created)` aggregation + optional sparse-series filling in Python
- CSV export streams via iterator chunking

## Redis caching strategy
Cache aggregated responses per endpoint + filter signature + user scope:
- key payload includes endpoint namespace, sorted query params, `user_id`, role scope (`partner_id`, `center_id`), `is_superuser`
- hash payload with `sha256`
- TTL 300s for dashboards

## Recommended PostgreSQL indexes
```sql
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_mscc_registration_created ON mscc_registration (created);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_mscc_registration_partner_created ON mscc_registration (partner_id, created);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_mscc_registration_center_created ON mscc_registration (center_id, created);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_mscc_registration_deleted_created ON mscc_registration (deleted, created);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_child_gender ON child_child (gender);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_child_nationality ON child_child (nationality_id);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_child_birthday_year ON child_child (birthday_year);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_educationservice_registration_latest ON mscc_educationservice (registration_id, id DESC);
```
