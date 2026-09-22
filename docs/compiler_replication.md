# Compiler → BMA-NFE replication

Partners enter MSCC data once, in the Compiler. This integration copies it
into BMA-NFE automatically so nobody has to key the same registration twice.

The channel is **one-way**. The Compiler is the system of record; BMA-NFE
holds a replica and never pushes anything back.

## What is replicated

Every MSCC table that exists in both systems. Field names are identical
between the two for all but the first three.

| Compiler model | Resource name | BMA-NFE model |
| --- | --- | --- |
| `mscc.Round` | `mscc.round` | `mscc.Round` |
| `mscc.Packages` | `mscc.package` | `mscc.Packages` |
| `locations.Center` | `locations.center` | `locations.Center` |
| `students.Teacher` | `mscc.teacher` | `mscc.Teacher` |
| `mscc.Registration` (+ child, services checklist, education history) | `mscc.registration` | `mscc.Registration` (+ `child.Child`, `mscc.ProvidedServices`, `mscc.EducationHistory`) |
| `mscc.EducationService` (child education situation) | `mscc.education_service` | same |
| `mscc.EducationRSService` | `mscc.education_rs_service` | same |
| `mscc.EducationAssessment` | `mscc.education_assessment` | same |
| `mscc.EducationProgrammeAssessment` (grading) | `mscc.education_grading` | same |
| `mscc.Referral` | `mscc.referral` | same |
| `mscc.PSSService` | `mscc.pss_service` | same |
| `mscc.InclusionService` | `mscc.inclusion_service` | same |
| `mscc.DigitalService` | `mscc.digital_service` | same |
| `mscc.HealthNutritionService` | `mscc.health_nutrition_service` | same |
| `mscc.HealthNutritionReferral` | `mscc.health_nutrition_referral` | same |
| `mscc.YouthKitService` | `mscc.youth_kit_service` | same |
| `mscc.YouthService` | `mscc.youth_service` | same |
| `mscc.YouthAssessment` | `mscc.youth_assessment` | same |
| `mscc.YouthReferral` | `mscc.youth_referral` | same |
| `mscc.FollowUpService` | `mscc.follow_up_service` | same |
| `mscc.Recreational` | `mscc.recreational` | same |
| `mscc.LegoService` | `mscc.lego_service` | same |
| `attendances.MSCCAttendance` + its child rows | `attendances.mscc_attendance` | `attendances.MSCCAttendance` + `MSCCAttendanceChild` |

Three tables travel **inside the registration** rather than as resources of
their own, because BMA-NFE never generates them — the Compiler does, and this
side only reads them to draw the child profile:

* `child.Child` — a change to a child republishes every registration that
  carries it.
* `mscc.ProvidedServices` — the services checklist. It is replaced as a set on
  every registration push, which is exactly what the Compiler's
  `regenerate_services` does. Its `service_id` column is a local primary key
  in both databases: the Compiler sends which record it points at as a
  natural key and this side resolves it through the mapping. If the service
  itself has not arrived yet, the reference is kept on the registration's
  `SyncedRecord.pending_links`, and the service completes the link when it
  lands — only if it is the record the row was meant for, which matters for
  "Health and Nutrition", a row two different tables can complete. Saving a
  service in the Compiler republishes the registration as well, so a
  completed checklist item arrives within moments.
* `mscc.EducationHistory` — `child` and `registration_id` are bare integer
  columns; they are filled from local ids here. `programme_id` refers to the
  Compiler's CLM tables (BLN, ABLN, …), which do not exist here, so the
  "programme details" link on the profile will not resolve for replicated
  lines.

Scope is the whole MSCC module — every record, every partner, every round.

Not replicated, on purpose: the CLM/Dirasa attendance tables (not MSCC),
`RoundPartner` and `NFEToFEReferralMapping` (BMA-NFE only), and the
administrative geography (`Location`), which is master data both systems are
expected to already share and is matched by P-code rather than copied.

## How a change gets across

1. A partner saves a record in the Compiler.
2. A `post_save` receiver writes a row into the Compiler's outbox
   (`datasync.SyncEvent`) inside the same database transaction.
3. Once that transaction commits, the Compiler pushes the record to
   `POST /api/sync/events/` here. Pressing Save is what sends it — by default
   the Compiler's web process makes the call itself, so nothing waits on a
   worker or a scheduler.
4. This side applies the event, links it to the local row in
   `datasync.SyncedRecord`, and reports the outcome per event.
5. A Celery beat sweep on the Compiler re-sends anything that failed. That
   sweep is a retry net only, not how changes normally arrive.

Because the payload is built at delivery time rather than at save time, what
arrives is always the record's latest state, and a burst of edits collapses
into one push.

## The wire contract

`POST /api/sync/events/`, authenticated with the DRF token of a service
account in the `DataSync` group.

```json
{
  "source_system": "compiler",
  "contract_version": "1.0",
  "events": [
    {
      "event_id": "0f1a...uuid4",
      "resource": "mscc.registration",
      "operation": "upsert",
      "source_id": 1234,
      "source_modified": "2026-08-30T09:15:00Z",
      "payload": {
        "fields": {"have_labour": "No", "type": "Core-Package"},
        "center": {"source_id": 41, "p_code": "LB-0301", "name": "Makani Tripoli",
                   "partner": {"name": "Partner One"}},
        "round": {"source_id": 3, "name": "2026 Round A", "year": 2026},
        "partner": {"name": "Partner One"},
        "child": {"source_id": 900, "fields": {"unicef_id": "UNI-900", "...": "..."}}
      }
    }
  ]
}
```

The reply reports every event separately:

```json
{
  "applied": 1, "skipped": 0, "failed": 0,
  "results": [
    {"event_id": "0f1a...", "resource": "mscc.registration", "source_id": 1234,
     "status": "applied", "local_id": 88, "conflict": false,
     "retryable": false, "ignored_fields": ["child_is_idp"], "detail": ""}
  ]
}
```

* `status` is `applied`, `skipped` (already seen) or `failed`.
* `retryable: true` means a parent record had not arrived yet; the Compiler
  sends the event again rather than dropping it.
* `ignored_fields` lists columns the Compiler has and BMA-NFE does not.
* `conflict: true` means the update overwrote values a BMA-NFE user had
  edited; see *Conflicts* below.

`GET /api/sync/events/` returns a capability document and is the quickest way
to confirm the URL and token from the Compiler side.

### No shared primary keys

The two databases were never seeded together, so nothing crosses the wire as
a local id. Relations travel as natural keys and are resolved here:

| Relation | Matched on |
| --- | --- |
| Round | sync mapping, then unique name — created if missing |
| Centre | sync mapping, then P-code, then name + partner — a stub is created if missing |
| Partner organization | unique name — created if missing |
| School | CERD number, then name — never created |
| Location (governorate / caza / cadaster) | P-code, then name — never created |
| Nationality, ID type, disability, educational level | name — never created |
| Training topic, attachment type | name — created if missing |
| Child | sync mapping, then UNICEF unique id |
| Registration | sync mapping only |

Anything left unresolved is reported in the event's `detail` and the field is
left empty, rather than the whole record being rejected. Set
`DATASYNC_CREATE_MISSING_REFERENCES=False` to stop even the placeholder
creation, at the cost of registrations arriving without a centre.

## Conflicts

The Compiler always wins. BMA-NFE users are not blocked from editing a
replicated record, but every field the sync overwrites that a local user had
changed is recorded in **Data replication → Sync conflicts**, with the value
the sync last wrote and the value the local user had put there. Mark a
conflict reviewed once it has been dealt with — normally by re-entering the
change in the Compiler, which is the record's real home.

Conflict detection works from a snapshot of the fields the sync wrote, stored
on the mapping row, so a field nobody touched never raises one.

## Setup on this side

1. Create the service account and print its token:

   ```
   python manage.py datasync_create_client
   ```

   It creates the `compiler-sync` user, puts it in the `DataSync` group and
   issues a DRF token. Pass `--rotate` to replace a lost or leaked token.

2. Give the Compiler the token and the endpoint URL
   (`https://<this-host>/api/sync/events/`).

3. Settings, all overridable from the environment:

   | Setting | Default | Meaning |
   | --- | --- | --- |
   | `DATASYNC_INGEST_ENABLED` | `True` | Off makes the endpoint answer 503; the Compiler queues and retries |
   | `DATASYNC_CLIENT_GROUP` | `DataSync` | Group a service account must be in |
   | `DATASYNC_ALLOWED_SOURCE_SYSTEMS` | `['compiler']` | Producers accepted |
   | `DATASYNC_MAX_BATCH_SIZE` | `200` | Events per request |
   | `DATASYNC_CREATE_MISSING_REFERENCES` | `True` | Allow placeholder rounds, centres, partners and free-text lookups |

## Operating it

Everything lives under **Data replication** in the Django admin:

* **Sync events** — every event received, with its status and detail. Filter
  by `failed` to see what is not getting in.
* **Synced records** — which Compiler id maps to which local row.
* **Sync conflicts** — local edits an update overwrote.

Turning the ingest off is safe: the Compiler keeps queueing and drains once it
is back on. Nothing is lost unless its outbox is cleared.

## Known limits

* **Teachers are a lossy mapping.** The Compiler stores teachers per *school*
  (`students.Teacher`, a Dirasa concept) while BMA-NFE stores them per
  *centre*. The Compiler translates the fields it can — the three birthday
  columns into `birthdate`, `teaching_hours_dirasa` into
  `teaching_hours_mscc`, "Dirasa only" into "Makani only" — and takes the
  centre from an operator-maintained school-to-centre table on its side.
  Until a school is mapped there, its teachers arrive without a centre.
  `years_of_experience` and `training_date_of_completion` have no source in
  the Compiler and stay empty.
* **Uploaded files are not copied.** Teacher attachments travel as their
  description and type only; the files themselves stay in the Compiler.
* **Grading covers the shared sheet only.** The Compiler also has
  `EducationProgrammeWLAssessment`, `EducationProgrammeSummerRSAssessment` and
  `TarlAssessment`, which have no counterpart here and are not replicated.
  Its `EducationProgrammeAssessment` fields `mid_test`, `youth_pre_test` and
  `youth_post_test` are reported as ignored for the same reason.
* **Compiler-only columns are dropped, by design** — for example
  `Registration.child_is_idp`, `Registration.consent`,
  `EducationService.ppl_sector`, `Center.is_tarl`, `DigitalService.madrasti`,
  `LegoService.participating_lego_events`. They appear in each event's
  `ignored_fields` so the loss is visible rather than silent.
* **Some choice lists are longer in the Compiler.** Values such as
  `Summer RS Grade 1` (attendance / education programme), `SDC` (centre type)
  and the "Internally Displaced …" education statuses are stored here as sent
  — Postgres does not enforce choices — but will not appear in BMA-NFE's own
  dropdowns until they are added to its choice lists.
