# Compiler → BMA-NFE replication

Partners enter MSCC data once, in the Compiler. This integration copies it
into BMA-NFE automatically so nobody has to key the same registration twice.

The channel is **one-way**. The Compiler is the system of record; BMA-NFE
holds a replica and never pushes anything back.

## What is replicated

| Compiler model | Resource name | BMA-NFE model |
| --- | --- | --- |
| `mscc.Round` | `mscc.round` | `mscc.Round` |
| `locations.Center` | `locations.center` | `locations.Center` |
| `students.Teacher` | `mscc.teacher` | `mscc.Teacher` |
| `mscc.Registration` | `mscc.registration` | `mscc.Registration` |
| `mscc.EducationService` (child education situation) | `mscc.education_service` | `mscc.EducationService` |
| `mscc.EducationProgrammeAssessment` (grading) | `mscc.education_grading` | `mscc.EducationProgrammeAssessment` |
| `mscc.Referral` | `mscc.referral` | `mscc.Referral` |
| `attendances.MSCCAttendance` + its child rows | `attendances.mscc_attendance` | `attendances.MSCCAttendance` + `MSCCAttendanceChild` |

`child.Child` is not a resource of its own: a child travels inside the
registration that refers to it, and a change to a child republishes every
registration that carries it.

Scope is the whole MSCC module — every record, every partner, every round.

## How a change gets across

1. A partner saves a record in the Compiler.
2. A `post_save` receiver writes a row into the Compiler's outbox
   (`datasync.SyncEvent`) inside the same database transaction.
3. Once that transaction commits, a Celery task pushes the record to
   `POST /api/sync/events/` here. If the broker is unreachable the push runs
   in the web process instead, so the record still arrives immediately.
4. This side applies the event, links it to the local row in
   `datasync.SyncedRecord`, and reports the outcome per event.
5. A Celery beat sweep on the Compiler re-sends anything that failed.

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
  `EducationService.ppl_sector`, `Center.is_tarl`. They appear in each event's
  `ignored_fields` so the loss is visible rather than silent.
