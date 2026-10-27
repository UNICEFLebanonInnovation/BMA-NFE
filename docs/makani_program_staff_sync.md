# Makani ProgramStaff sync

Compiler `locations.ProgramStaff` is the source for BMA-NFE's existing
`mscc.Teacher` table. Dirasa `students.Teacher` is no longer a sync source.
No additional teacher table or sync endpoint is introduced.

## Mapping

| Compiler ProgramStaff | NFE Teacher |
| --- | --- |
| `id` | `bma_id`, with `bma_source=locations.program_staff` |
| `center` | Centre resolved by its Compiler BMA ID |
| `facilitator_name` | `facilitator_name`, preserving up to 200 characters |
| `gender` | `sex` |
| `phone_number` | `primary_phone_number` |
| `email` | `email`, up to 254 characters |
| `weekly_hours_taught` | `teaching_hours_mscc` |
| `subject`, `programs`, `training_topics`, `attendance_training`, `is_active_current_round` | Exact values in `program_staff_details` JSON |

The facilitator name is displayed in the existing NFE Teachers list. No
first/father/last names, birthday or round are invented from the source name.
ProgramStaff has no round association. Teacher assignment is `Makani only`.
CV and diploma files are outside the child-photo contract and are not copied.

## Selection and Makani boundaries

In **Data replication → Bulk sync**, select a partner and any combination of
categories. **Teachers (Makani program staff)** selects that partner's staff
through their direct centre relationship. Centres and staff work without a
round; registration-dependent categories require a round.

The same eligibility policy is used for previews, queue preparation, automatic
saves, backfills, photo linking and the last check before delivery:

- Registration package types `Core-Package`, `Walk-in`, historical
  `Walk-in-OOSC` / `Walk-in-In-School`, and historical blank/null types are
  treated as Makani. Blank/null handling preserves the existing Makani-list
  treatment. `TLS`, Dirasa and unknown package types are excluded.
- Education services, assessments, grading and referrals require an eligible
  Makani registration. TLS-only child/Student edits enqueue no events or photos.
- TLS-only centres are excluded. A centre marked TLS may also provide Makani:
  an eligible registration or staff with an explicit Makani programme keeps
  that shared centre eligible. Unmarked centres retain their Makani treatment.
- Known ProgramStaff programmes are BLN, ABLN, RS, CBECE, YBLN and YFS.
  Unknown programmes are excluded. Staff without a centre cannot be selected.
- A whole attendance day is excluded if any row lacks an eligible Makani
  registration. A mixed Makani/TLS day must be corrected or split at the source;
  its rows are never partially sent or silently removed on NFE.
- Shared round metadata carries no TLS or other-partner child data.

Partner ownership and requester permissions are still checked again at
delivery. A queued registration changed to TLS is blocked before HTTP or
photo reads. Old `mscc.teacher` events are blocked, never reinterpreted as
ProgramStaff IDs. Legacy deletions without proven scope require review.

## Identity, delivery and storage

Events use resource `locations.program_staff` and source marker
`locations.programstaff`. NFE identifies a ProgramStaff record by source type
and BMA ID. A centre move updates the same teacher row. A database uniqueness
constraint prevents duplicates, including concurrent first deliveries.

The legacy teacher ID sequence is separate. Existing rows receive the legacy
source tag, so ProgramStaff #1 cannot overwrite an old Dirasa Teacher #1.
Existing legacy rows are retained for review; this change does not clean up
previously imported test data. NFE rejects new legacy teacher events and TLS
registration payloads. Previously applied event-ID replays remain idempotent.

All delivery still uses `/api/sync/events/`, the existing outbox, worker,
dependency order, retries, HTTP pools and controlled photo upload concurrency.
Registration photos keep verified reuse: an unchanged target photo uploads
zero image bytes. Compiler Azure storage and NFE file-share storage settings
are unchanged by this correction.

## Deployment

1. Deploy BMA-NFE and run its normal `python manage.py migrate`. This adds
   `datasync.0009`, `mscc.0019` and `mscc.0020`.
2. Deploy Compiler and run its normal `python manage.py migrate`, including
   partner selection migration `datasync.0008` if pending, then `0009`.
3. Restart web apps and Compiler Celery workers/beat so old processes cannot
   continue publishing Dirasa teachers.
4. For restricted operators, grant `locations.view_programstaff` (or change)
   in place of Dirasa teacher permission, plus the existing partner, centre
   and bulk-run permissions. Staff with a partner/centre assignment remain
   restricted to it.
5. Preview and start a new partner-scoped bulk request. Old requests which
   explicitly selected `mscc.teacher` remain historical and cannot be reused
   to select ProgramStaff. Old pending teacher events are parked by the
   normal permanent-failure retry policy.

## Verification, 27 October 2026

Local tests used the original clones, PostgreSQL and isolated settings:
145 Compiler sync tests and 150 NFE sync tests passed. NFE migrations were
applied to the local demo database; both model/migration drift checks passed.

Actual browser and HTTP checks created synthetic Makani/TLS fixtures:

- All-categories browser run `c7b39fd9-265e-47e1-97ad-30745bc53429`: nine
  deliveries; TLS centre, child, registration, services and attendance absent.
- A same-number legacy teacher survived unchanged alongside ProgramStaff.
- Normal ProgramStaff form creation produced one event. Form editing preserved
  a name longer than 64 characters, changed hours, and audited an overwritten
  local NFE edit without duplicating the teacher.
- Repeated run `97e8835b-fa74-48f7-af90-c647e0d8d5dd`: ten deliveries after
  adding another staff member; zero uploaded photo bytes and no duplicate rows.
- Master run `6ef54fbe-fa08-4d70-aa49-ef77eac5daf6`: centre and two staff
  delivered without a round. The browser disables the round selector for
  this category combination.
- Normal TLS registration, child, Student-photo and Dirasa teacher admin
  saves produced no events. Authenticated NFE HTTP requests for legacy teacher
  and TLS registration payloads were rejected without modifying ProgramStaff.
- NFE's existing Teachers list visibly displayed the received facilitator.

These checks verify local application behavior. Azure connectivity and the VM
file-share mount must be verified in the deployment environment.

![Completed centre and ProgramStaff sync](images/makani-program-staff-completed.png)

## NFE teacher portal verification

The imported facilitator name is read-only on the existing teacher edit screen.
Contacts can be edited without supplying split names, a round or legacy
qualifications that ProgramStaff does not provide. Locally entered teachers
retain their existing requirements. Name search supports Unicode and
case-insensitive matching. Direct edit/delete URLs and centre choices enforce
the same partner/centre scope as the teacher list.

[Completed portal validation: 51 end-to-end checks and 338 regressions](teacher_portal_validation_2026-10-27.md).
