# NFE teacher portal validation — 27 October 2026

**51 focused end-to-end checks passed. All 338 regression tests passed.**

The pending ProgramStaff form and search correction is now saved in the original BMA-NFE checkout and verified.
The earlier usage-limit block is resolved. No local portal issue remains from this audit.

## Method

Testing used both original repositories, isolated local PostgreSQL databases, the actual web applications,
normal CSRF-protected forms, authenticated HTTP, the real Compiler outbox/Celery worker and NFE ingestion.
Browser checks saved an NFE contact change, saved the authoritative Compiler update, and applied the new name filter.
Repeated and concurrent form submissions used HTTP against those same running views. Nothing was mocked in these checks.
Temporary role accounts and two scope records were prepared with controlled model operations in the local test database.

## Fixes completed

- Imported ProgramStaff displays the authoritative full name as read-only. Missing split names, round and legacy qualifications no longer block contact edits. Existing locally entered teachers keep their original required fields.
- Contact edits preserve an absent or existing NFE-owned UNICEF reference; the form does not generate one from fields absent in ProgramStaff.
- Teacher lists, direct edit URLs and delete URLs now enforce the same centre/partner scope. Form centre choices respect that scope, and a form opened before access revocation cannot submit afterward.
- Accounts without a Makani role receive 403 instead of an authentication-mixin server error; unauthenticated visitors still go to the configured login entry point.
- NFE supports case-insensitive facilitator-name search alongside the existing first-name and centre filters.

## Data and repeatability checks

- The same synthetic teacher retained its Compiler BMA ID and NFE primary key through every edit and resync.
- Full 200-character Arabic names and long email addresses remained intact. Forged disabled-name and BMA-identity fields did not change the protected values.
- Compiler edits overwrote local NFE contact edits and produced the expected conflict audit. Programme arrays, flags, centre and no-round state remained correct.
- Ten simultaneous NFE saves completed without duplication. Ten simultaneous Compiler saves each created a durable event and converged on the latest source value.
- Repeating the 200-photo import completed all 202 events, retained 200 registrations and uploaded zero image bytes.
- Filtered CSV export contained exactly the selected facilitator, its full Unicode name and restored contact values.
- The final audit found one target identity and no unresolved source events for the tested staff. All five temporary role accounts were disabled and their passwords made unusable.

## Automated checks

| Suite | Passed |
| --- | --- |
| Compiler datasync | 150 |
| NFE datasync and related MSCC access/form tests | 188 |
| Total | 338 |

Django checks and migration-state checks passed. The only Django check warning is the pre-existing local debug-toolbar middleware warning.

## Passed end-to-end scenarios

| # | Scenario |
| --- | --- |
| 1 | Browser: NFE contact save succeeds with a 200-character name, blank split names and no round |
| 2 | Browser contact edit preserves BMA identity, source full name and programme data |
| 3 | Browser: Compiler update overwrites the NFE phone/email edit on the same teacher and records the conflict |
| 4 | NFE edit page loads without validation errors and shows the source name as read-only |
| 5 | Forged disabled name and hidden identity fields cannot change the synced name or BMA identity |
| 6 | Invalid form: invalid phone preserves the complete existing teacher |
| 7 | Invalid form: invalid email preserves the complete existing teacher |
| 8 | Invalid form: missing centre preserves the complete existing teacher |
| 9 | NFE edit accepts empty optional email and zero hours while preserving source programme data |
| 10 | Next Compiler form save restores authoritative values and audits local NFE contact changes |
| 11 | Repeating ProgramStaff bulk sync preserves the target ID and produces no false conflict |
| 12 | NFE search: full-name prefix finds exactly the synced facilitator |
| 13 | NFE search: case-insensitive prefix finds exactly the synced facilitator |
| 14 | NFE search: Arabic text finds exactly the synced facilitator |
| 15 | NFE search: entire 200-character name finds exactly the synced facilitator |
| 16 | NFE search: no-match query returns an empty list |
| 17 | NFE search safely handles quote and markup-like input without broadening results |
| 18 | NFE name and centre search filters combine correctly |
| 19 | Clearing the new name filter restores the regular teacher list |
| 20 | centre: teacher list includes exactly the authorized records |
| 21 | centre: direct own-teacher edit follows the same access scope |
| 22 | centre: foreign edit/delete URLs return 404 and preserve the foreign record |
| 23 | centre: forged foreign centre POST is rejected without changing the teacher |
| 24 | centre: a valid own form cannot be submitted to a foreign teacher URL |
| 25 | partner: teacher list includes exactly the authorized records |
| 26 | partner: direct own-teacher edit follows the same access scope |
| 27 | partner: foreign edit/delete URLs return 404 and preserve the foreign record |
| 28 | partner: forged foreign centre POST is rejected without changing the teacher |
| 29 | partner: a valid own form cannot be submitted to a foreign teacher URL |
| 30 | unassigned: teacher list includes exactly the authorized records |
| 31 | unassigned: direct own-teacher edit follows the same access scope |
| 32 | unassigned: foreign edit/delete URLs return 404 and preserve the foreign record |
| 33 | unicef: teacher list includes exactly the authorized records |
| 34 | unicef: direct own-teacher edit follows the same access scope |
| 35 | Local teacher creation still requires the original split-name and qualification fields |
| 36 | An authenticated account without a Makani role cannot list or edit teachers |
| 37 | A valid local teacher can still be created through the normal form with the original schema |
| 38 | Normal local-teacher edits still work and retain a local identity |
| 39 | Required local-teacher names remain required during edit |
| 40 | The original first-name search still finds local teachers correctly |
| 41 | An unauthenticated visitor is redirected to login before teacher details are read |
| 42 | Teacher contact edits without a CSRF token are rejected |
| 43 | Ten concurrent NFE form saves finish without errors, duplicate teachers or damaged source identity |
| 44 | Compiler sync restores its current contact value after concurrent NFE edits |
| 45 | Ten rapid concurrent Compiler form saves each produce a durable event and converge on the latest source data |
| 46 | Repeat 200-photo integration run still sends 202 records, uploads zero image bytes and keeps 200 registrations |
| 47 | An already-open form cannot edit a teacher after the user is moved to another centre |
| 48 | Imported-staff contact save preserves an absent NFE reference instead of generating an ID from missing names |
| 49 | Imported-staff contact save preserves an existing NFE reference instead of generating an ID from missing names |
| 50 | Filtered CSV export includes exactly one facilitator with its full Unicode name and restored contact data |
| 51 | Final audit: correct mapped values, one teacher identity, no unresolved delivery and all five test accounts disabled |

## Contract and deployment boundary

The 11 source-only fields remain excluded under the confirmed existing contract. The portal correction adds no columns or new sync pipeline and does not change Compiler Azure storage; the existing sync migrations remain required.
SIT still needs the deployment smoke test for actual Azure connectivity, the VM file-share mount/permissions/persistence and deployed worker versions. Local tests cannot verify that mount.

![Verified NFE form](images/teacher-portal-readonly-name.png)

[Machine-readable results](teacher_portal_validation_2026-10-27.json)

[Original bulk/photo and shared-field audit](manual_sync_validation_2026-10-27.md)
