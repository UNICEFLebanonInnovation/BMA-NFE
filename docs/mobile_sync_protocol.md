# BMA Mobile Sync Protocol

This document specifies the API contract between the BMA-NFE platform and the
BMA mobile application (Flutter, tablet/phone, offline-first with a local
SQLite database). It is implemented on the server side by the
`student_registration.mobile_api` Django app and on the client side by the
`BMA-App` repository.

The protocol has four pillars:

1. **Login** – token authentication and a role/scope profile.
2. **Bootstrap** – reference data, choice lists and *form schemas* that let the
   app render every registration/service form exactly as the web platform does.
3. **Pull** – incremental download of the records the user is allowed to see.
4. **Push** – batched upload of offline work with server-side verification,
   duplicate detection and a per-item report that the field worker reviews
   (merge / link / create anyway / discard).

All endpoints live under `/api/mobile/v1/` and speak JSON. Times are ISO-8601
in UTC (`2026-09-12T08:15:30Z`). Authentication uses DRF token auth:
`Authorization: Token <token>`.

---

## 1. Authentication

### `POST /api/mobile/v1/auth/login/`

```json
{
  "username": "center_user",
  "password": "********",
  "device_id": "5f0c6f2e-...",          // stable per installation (UUID)
  "device_name": "Samsung Tab A8",
  "app_version": "1.0.0+1"
}
```

Response `200`:

```json
{
  "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
  "server_time": "2026-09-12T08:15:30Z",
  "user": {
    "id": 12, "username": "center_user", "first_name": "…", "last_name": "…",
    "email": "…", "language": "ar",
    "groups": ["MSCC_CENTER"],
    "partner": {"id": 3, "name": "Partner NGO"},
    "center": {"id": 41, "name": "Makani Center – Bar Elias"},
    "school": null,
    "schools": [],
    "modules": {
      "mscc": {"enabled": true,  "can_register": true, "can_attend": true, "can_edit": true},
      "alp":  {"enabled": false, "can_register": false, "can_attend": false, "can_edit": false},
      "clm":  {"enabled": false, "can_register": false, "can_attend": false, "can_edit": false}
    }
  }
}
```

`modules` mirrors the `group_required` rules of the web views (see
`docs/ACCESS_CONTROL.md`). The app hides modules the user cannot use.

`401` on bad credentials, `403` when the account is inactive. Only one active
token exists per user (`rest_framework.authtoken`); logging in again on another
device re-uses the same token (the web platform's one-session rule is not
applied to mobile).

### `POST /api/mobile/v1/auth/logout/` – deletes the token.
### `GET  /api/mobile/v1/me/` – returns the `user` block above.

---

## 2. Bootstrap

### `GET /api/mobile/v1/bootstrap/`

Returns everything the app needs to work offline **except** beneficiary
records:

```json
{
  "server_time": "…",
  "reference": {
    "nationalities":     [{"id": 1, "name": "Syrian", "name_en": "Syrian"}],
    "locations":         [{"id": 7, "name": "بعلبك", "name_en": "Baalbek", "type": "district", "parent_id": 2, "p_code": "…"}],
    "partners":          [{"id": 3, "name": "…"}],
    "centers":           [{"id": 41, "name": "…", "partner_id": 3, "location_id": 7}],
    "schools":           [{"id": 900, "number": "1234", "name": "…", "location_id": 7, "is_bma": true}],
    "rounds":            {"mscc": [{"id": 5, "name": "2025-2026", "current_year": true}], "alp": [...], "clm": [...]},
    "packages":          [{"id": 1, "category": "Education", "type": "…", "name": "…"}],
    "disabilities":      [...], "id_types": [...], "education_levels": [...],
    "alp_grading_definitions": [...]
  },
  "choices": {
    "mscc.attendance.education_program": [{"value": "BLN Level 1", "label": "BLN Level 1"}, ...],
    "mscc.attendance.class_section": [...], "mscc.attendance.absence_reason": [...],
    "mscc.attendance.close_reason": [...], "alp.attendance.absence_reason": [...],
    "alp.attendance.close_reason": [...], "alp.teacher_attendance.status": [...],
    "clm.attendance.registration_level": [...], "clm.attendance.absence_reason": [...],
    "clm.attendance.close_reason": [...], "child.gender": [...], "yes_no": [...]
  },
  "schemas": {
    "mscc.registration": {
      "key": "mscc.registration", "module": "mscc", "label": "Registration", "kind": "identity",
      "parent": null, "identity": true, "multiple": true, "pullable": true, "wizard": true,
      "confirm_fields": ["first_phone_number", "second_phone_number"],
      "sections": [
        {"key": "identity", "label": "Identity", "label_ar": "الهوية", "fields": ["child_first_name", "child_father_name", ...]},
        {"key": "caregivers", "label": "Caregivers & household", "label_ar": "...", "fields": [...]},
        {"key": "labour", "label": "Child labour", "label_ar": "...", "fields": [...]}
      ],
      "fields": [
        {"name": "child_first_name", "label": "Child's First Name", "label_ar": "...", "type": "text",
         "required": true, "max_length": 64, "help_text": "", "placeholder": "مثال: محمد"},
        {"name": "child_gender", "label": "Gender", "type": "select", "required": true,
         "choices": [{"value": "", "label": "----------"}, {"value": "Male", "label": "Male", "label_ar": "ذكر"}, ...]},
        {"name": "child_nationality", "label": "Nationality", "type": "ref", "ref": "nationalities", "required": true},
        {"name": "labour_condition", "label": "…", "type": "multiselect", "choices": [...]},
        {"name": "registration_date", "type": "date", ...},
        {"name": "case_number", "type": "text", "pattern": "^(245|380|...)-\\d{2}[C-](\\d{5}|\\d{6})$"}
      ],
      "reveals": [
        {"when": {"field": "have_labour", "not_in": ["", "No"]}, "show": ["labour_type", "labour_hours", ...]},
        {"when": {"field": "id_type", "in": ["5"]}, "show": ["parent_national_number", "national_number", ...]}
      ]
    },
    "mscc.pss": {...}, "mscc.new_round": {...}, "alp.registration": {...}, "clm.bridging": {...}
  },
  "entities": ["mscc.registration", "mscc.education_service", "..."]
}
```

Schemas are generated **from the Django form classes** used by the web
platform (`MainForm`, `PSSServiceForm`, `EducationServiceForm`, …). Labels,
choices, `required` flags and max lengths therefore always match the website,
and adding a field to a web form automatically exposes it to the app. Layout
overlays (sections, conditional reveals) are declared in
`mobile_api/registry.py`.

Field `type` is one of `text`, `textarea`, `number`, `decimal`, `date`,
`datetime`, `email`, `boolean`, `select`, `multiselect`, `ref` / `multiref`
(foreign key to a `reference` list, e.g. `nationalities`, `rounds.mscc`,
`alp_programs`; `parent` means the owning registration), `file`, `hidden`.
Choices are inlined on each field (`value`, `label`, `label_ar`). `reveals`
describe conditional visibility (`in`, `not_in`, `label_contains`).

Entity kinds: `identity` (registration forms, duplicate-checked), `form`
(MSCC service forms), `modelform` (ALP teacher/grading/school profile),
`teacher` (MSCC teacher), `new_round`, `bridging_subform` (post/mid
assessment, follow-up, services – they update the Bridging row),
`school_activity` (clubs, meetings, initiatives, health visits), `attendance`
and `teacher_attendance`.

---

## 3. Pull (server → device)

### `GET /api/mobile/v1/pull/?since=<iso>&entities=<csv>&cursor=<n>&limit=500`

Returns changed records for the requested entities (default: all entities
the user's modules allow), **scoped exactly like the web list views**
(centre user → own centre, partner user → own partner, school user → own
school, UNICEF/staff → everything).

```json
{
  "server_time": "…",
  "changes": [
    {"entity": "mscc.registration", "server_id": 8812, "modified": "…", "deleted": false,
     "data": {"id": 8812, "child": {"id": 5120, "first_name": "…", "unicef_id": "…", ...},
              "center": 41, "partner": 3, "round": 5, ...}},
    {"entity": "mscc.education_service", "server_id": 4401, "parent_id": 8812, "modified": "…", "deleted": false, "data": {...}},
    {"entity": "mscc.attendance_day", "server_id": 77, "modified": "…", "deleted": false,
     "data": {"round_id": 5, "center_id": 41, "attendance_date": "2026-09-10", "education_program": "…",
              "class_section": "…", "attendance_day_off": "No", "close_reason": "",
              "children_attendance": [{"registration_id": 8812, "child_id": 5120, "attended": "Yes",
                                        "absence_reason": null, "absence_reason_other": null}]}}
  ],
  "next_cursor": "500",
  "has_more": true
}
```

`since` omitted → full download. The device stores `server_time` of a
completed pull as the next `since`. Deleted/soft-deleted records are returned
with `deleted: true` so the device can hide them.

Registration data always embeds the child (or, for CLM, the `student`) so a
single record is enough to render the profile and pre-fill edit forms.

---

## 4. Push (device → server)

### `POST /api/mobile/v1/push/`

```json
{
  "batch_uuid": "c0a8…",              // generated on the device; makes the call idempotent
  "device_id": "5f0c6f2e-…",
  "app_version": "1.0.0+1",
  "items": [
    {
      "client_uuid": "1e6c…",
      "entity": "mscc.registration",
      "op": "create",                 // create | update | delete
      "server_id": null,              // set for update/delete
      "parent_uuid": null,            // for child records created offline in the same batch
      "parent_id": null,              // or the server id of an already-synced parent
      "base_modified": null,          // server `modified` the edit was based on (update only)
      "client_modified": "…",
      "data": { ...form values exactly as posted by the web form... },
      "resolution": null              // see §4.3
    },
    {
      "client_uuid": "9a12…",
      "entity": "mscc.education_service",
      "op": "create",
      "parent_uuid": "1e6c…",
      "data": {"education_program": "…", "class_section": "…", "round": 5, "registration_date": "2026-09-01"}
    },
    {
      "client_uuid": "77aa…",
      "entity": "mscc.attendance_day",
      "op": "upsert",
      "data": {"round_id": 5, "attendance_date": "2026-09-10", "education_program": "…", "class_section": "…",
               "attendance_day_off": "No", "close_reason": "",
               "children_attendance": [{"registration_uuid": "1e6c…", "child_uuid": null, "attended": "No",
                                        "absence_reason": "Sick", "absence_reason_other": ""}]}
    }
  ]
}
```

Items are processed **in dependency order** (parents before children) inside
one database transaction *per item*, so one failing record never blocks the
rest of the batch. Re-sending a batch with the same `batch_uuid` returns the
stored report instead of re-applying it.

### 4.1 Result report

```json
{
  "batch_id": 318,
  "batch_uuid": "c0a8…",
  "received_at": "…",
  "summary": {"total": 3, "created": 1, "updated": 0, "merged": 0, "linked": 0,
              "duplicate": 1, "conflict": 0, "error": 1, "discarded": 0, "skipped": 0},
  "results": [
    {"client_uuid": "1e6c…", "entity": "mscc.registration", "status": "duplicate",
     "server_id": null, "message": "A child with the same identity already exists.",
     "duplicates": [
        {"registration_id": 8812, "child_id": 5120, "label": "Mohamad Ahmad Al Sayed",
         "mother_fullname": "…", "birthday": "2015-03-02", "gender": "Male", "nationality": "Syrian",
         "center": "Makani – Bar Elias", "partner": "…", "round": "2025-2026",
         "match": {"reason": "identity", "score": 1.0, "fields": ["names", "birthday", "gender"]}}
     ]},
    {"client_uuid": "9a12…", "entity": "mscc.education_service", "status": "skipped",
     "message": "Parent registration was not saved (duplicate)."},
    {"client_uuid": "77aa…", "entity": "mscc.attendance_day", "status": "error",
     "errors": {"attendance_date": ["Attendance date cannot be in the future."]}}
  ]
}
```

Statuses: `created`, `updated`, `merged`, `linked`, `duplicate`, `conflict`,
`error`, `discarded`, `skipped`, `deleted`.

Every successful result carries `data_after` with the server representation
of the saved row (for registrations: nested `child`/`student` with `id`,
`number`, `unicef_id`, plus `*_label` names and, for MSCC, an
`education_summary`) so the device can replace its temporary identifiers.
Two special cases: a `mscc.new_round` item answers with
`created_entity: "mscc.registration"` (the cloned registration), and a
Bridging sub-form answers with `updated_entity: "clm.bridging"`.

### 4.2 Duplicate verification (registrations only)

Executed for every `create` of an identity entity (`mscc.registration`,
`alp.registration`, `clm.bridging`) and for updates that change identity
fields. Candidates are searched among non-deleted registrations of the same
module, in this order:

1. **UNICEF unique id** – the same external Unique-ID service used by the
   website (`students.utils.generate_one_unique_id`). When the service is
   reachable and returns an id, any registration whose child carries the same
   `unicef_id` is a duplicate (`reason: "unicef_id"`).
2. **Identity key** – normalised `first_name + father_name + last_name +
   mother_fullname` (lower-cased, whitespace collapsed, Arabic alef/yaa/taa
   marbuta variants folded) **plus** birthday (day/month/year) **plus**
   gender (`reason: "identity"`). This runs even when the external service is
   down, so offline-collected data is always verified.
3. **Identity documents** – identical non-empty `id_number`,
   `national_number`, `individual_case_number`, `case_number`,
   `recorded_number`, `syrian_national_number`, `sop_national_number` or
   `other_number` (`reason: "id_number"`).
4. **Near match** – same normalised names and gender with a birth year that
   differs by at most one year (`reason: "near"`, `score < 1`). Reported so the
   field worker can decide; not blocking on its own unless another rule fires.

If any rule 1–3 matches, the item is returned as `duplicate` and **nothing is
written**. Children of that item in the batch are `skipped` and stay pending
on the device until the duplicate is resolved.

### 4.3 Resolutions

The device re-pushes the same item (same `client_uuid`) with a `resolution`:

| `resolution.action` | Meaning | Server behaviour | Result status |
|---|---|---|---|
| `merge` (`target_id` = registration id) | Same child, same registration | Copies every **non-empty** incoming child/registration value onto the existing records (existing non-empty values are only overwritten when `overwrite: true`). Dependent items in the batch are re-parented to the target. | `merged` |
| `link` (`target_id` = child id) | Same child, new enrolment (new centre/round) | Creates the registration for the **existing** child; no new child row. | `linked` |
| `create` | Different person despite the match | Creates child + registration; the item is flagged `duplicate_override` for audit. | `created` |
| `discard` | Offline record was a mistake | Nothing written; logged. Device marks the record discarded and, if `target_id` is given, maps the local record to that server id. | `discarded` |

### 4.4 Update conflicts

For `update` ops the device sends `base_modified`. If the server record was
modified after that timestamp by someone else the item returns `conflict` with
the current server `data`. The device shows a side-by-side view; re-pushing
with `resolution: {"action": "overwrite"}` applies the device version,
`{"action": "keep_server"}` drops the local change.

### 4.5 Attendance

Attendance documents (`*.attendance_day`) are idempotent upserts keyed on the
natural key (centre/school, round, date, programme, section). Only the child
rows included in the payload are touched, which mirrors the website's
`create_attendance` behaviour. Rows may reference registrations by server id
or by `registration_uuid` created in the same batch. Validation matches the
website: no future dates, mandatory absence reason when absent, `close_reason`
required on a day off.

### 4.6 Audit trail

Every batch is stored as `MobileSyncBatch` with one `MobileSyncItem` per
record (payload, status, errors, duplicates, resolution, resulting server id).

* `GET /api/mobile/v1/push/history/` – the user's last batches with summaries.
* `GET /api/mobile/v1/push/<batch_id>/` – the full report (used by the app's
  *Sync history* screen and by supervisors in the Django admin).
* `POST /api/mobile/v1/duplicates/check/` `{entity, data}` – optional online
  pre-check used by the registration wizard while connected; returns the same
  candidate list as a push would.

---

## 5. Device-side states

| Local state | Meaning |
|---|---|
| `synced` | Identical to the server. |
| `pending` | Created or modified offline, waiting for push. |
| `pushing` | Included in an in-flight batch. |
| `duplicate` | Server reported candidates; needs a resolution. |
| `conflict` | Server copy changed since the local edit; needs a resolution. |
| `error` | Validation failed; open the form, fix, re-push. |
| `discarded` | Resolved as discard; kept read-only for reference. |

The app never deletes local pending work automatically; only a resolution or
a successful push changes its state.

---

## 6. Security and scoping

* Every endpoint requires a valid token; scope filters are applied server-side
  on both pull and push – a centre user cannot push a registration for another
  centre even if the payload says so (`center`/`partner`/`school` are always
  taken from the user's profile, exactly like `MainForm.save`).
* Group checks reuse `has_group` from the web platform.
* Payload sizes: max 500 items per batch; the device splits larger outboxes.
* Photos/attachments are not synchronised in v1 (the web platform keeps them
  optional); the app stores a local path only.
