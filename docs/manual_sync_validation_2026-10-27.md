# Compiler / BMA-NFE sync validation — 27 October 2026

**86 passed scenario groups**, **147 shared fields compared**, and **338 automated regression tests passed**.

The audit used the original two checkouts, fresh synthetic records, the normal application/admin forms,
authenticated localhost HTTP, the actual Celery worker/beat, PostgreSQL and real files. Delivery was not mocked.
Browser interactions checked the bulk preview/start/completion and the NFE-served photo. Repeated form/API
operations were driven through HTTP to reproduce manual workflows. A 200-photo fixture and import/account
edge cases used controlled model setup in the isolated local databases. No production records or Azure services were used.

## Results

- Every supported category was created and edited through the actual forms; actual receiver payloads were compared against both databases.
- 200 photos: 200 child and registration identities, all image checksums and references verified. Initial upload: 435,400 image bytes.
- Repeating the 202-event import uploaded zero image bytes, preserved every child/photo path and created no duplicates.
- Four concurrent upload lanes were respected. Real repeated/concurrent receiver requests did not duplicate records.
- Ordinary and bulk sends enforce Makani eligibility. Partner/centre/round/child consistency is checked at dispatch and again on NFE.
- Receiver shutdown, unavailable target storage, unavailable source photo metadata, and a missing target file recovered as expected.
- Photo replacement, local NFE overwrite, clearing/restoring, checksum rejection and byte-for-byte retrieval passed.
- Attendance/referral/registration/staff deletions preserved unrelated identities, shared children and the legacy teacher namespace.
- Partner-restricted operator access, forged partner rejection, hidden foreign audits and CSRF checks passed.
- The temporary QA operator was disabled with an unusable password. Fault markers and held files were restored.
- No pending, failed or abandoned source events remained for the audited entity identities at the final audit.

## Defects found and repaired

1. A completed assessment incorrectly rejected a grade of zero. Both assessment screens now distinguish a missing grade from zero.
2. NFE optional blank assessment grades could reach int("") after creating a partial record. NFE now validates first and saves one complete record atomically.
3. Automatic sends bypassed relationship checks that existed for bulk runs. Registration centre/partner mismatches, cross-centre/round attendance, mismatched attendance children and inconsistent service rounds are now blocked before sending. Invalid Makani relationships keep a durable error event for correction/retry.
4. NFE now rejects the same invalid relationships independently and rolls back the whole event, including embedded child changes. A pre-existing unassigned centre can receive its explicitly supplied centre-partner reference; a known conflicting partner is rejected.

The original reproduction records were corrected and manually retested after repair. Regression tests cover zero/blank/missing grades and relationship rollback.

## Current contract exclusions

The receiver explicitly reports these Compiler fields as ignored because the current NFE schema has no corresponding columns.
They are not part of the 147 shared-field comparison. The user confirmed that these exclusions should remain in the current contract.

| Entity | Source fields not stored by current NFE schema |
| --- | --- |
| round | `end_date`, `start_date` |
| center_a | `active_during_emergency`, `is_tarl`, `is_tls`, `provide_french_language` |
| registration | `child_is_idp`, `child_outreach`, `consent` |
| service | `ppl_sector` |
| grading | `mid_test` |

## Passed scenarios

| # | Check |
| --- | --- |
| 1 | Normal ProgramStaff screen creates a Makani teacher with arrays, flags, hours and Arabic name |
| 2 | round: source values match actual wire payload and NFE row |
| 3 | center_a: source values match actual wire payload and NFE row |
| 4 | staff: source values match actual wire payload and NFE row |
| 5 | registration: source values match actual wire payload and NFE row |
| 6 | service: source values match actual wire payload and NFE row |
| 7 | assessment: source values match actual wire payload and NFE row |
| 8 | grading: source values match actual wire payload and NFE row |
| 9 | referral: source values match actual wire payload and NFE row |
| 10 | attendance: source values match actual wire payload and NFE row |
| 11 | Two rounds share one child, exact child data and byte-identical source photo |
| 12 | All centre, round, registration, child and attendance references resolve to the correct NFE local IDs |
| 13 | round: normal edit updates the existing target ID without duplication |
| 14 | center_a: normal edit updates the existing target ID without duplication |
| 15 | registration: normal edit updates the existing target ID without duplication |
| 16 | service: normal edit updates the existing target ID without duplication |
| 17 | grading: normal edit updates the existing target ID without duplication |
| 18 | referral: normal edit updates the existing target ID without duplication |
| 19 | attendance: normal edit updates the existing target ID without duplication |
| 20 | ProgramStaff edit replaces arrays, preserves zero hours, clears email and changes Yes to No |
| 21 | Child metadata updates both registrations and transfers zero unchanged photo bytes |
| 22 | Saving the source Student without changing the image reuses the existing target photo |
| 23 | Source image replacement saves exact green bytes on the existing NFE child |
| 24 | Normal education assessment edit transfers all post-test values including a zero grade |
| 25 | NFE normal assessment screen also accepts a completed grade of zero |
| 26 | NFE optional blank grades save safely without an error or a partial assessment |
| 27 | A subsequent Compiler assessment edit overwrites and audits the local NFE assessment edit |
| 28 | Editing an attendance child updates the existing target day and absence values |
| 29 | Partner name edits republish the correct embedded partner without changing its identity |
| 30 | Fresh TLS-only centre, child, Student photo, registration, service and Dirasa teacher create no sync events |
| 31 | TLS child/Student-photo/registration edits remain excluded and no TLS child exists in NFE |
| 32 | All-category bulk is partner/round/Makani scoped and leaves the other partner unchanged |
| 33 | Multiple master categories sync two centres and one ProgramStaff without a round |
| 34 | Two simultaneous clicks on the same bulk form create one durable request |
| 35 | A local NFE photo edit is detected and overwritten by the authoritative Compiler image |
| 36 | Clearing the source photo clears the NFE reference without duplicating the child |
| 37 | Re-upload after clearing restores the photo on the same NFE child |
| 38 | Cross-partner attendance: normal save is blocked before HTTP and preserves NFE data |
| 39 | Cross-partner attendance: correction delivers automatically to the same NFE row |
| 40 | Mismatched attendance child: normal save is blocked before HTTP and preserves NFE data |
| 41 | Mismatched attendance child: correction delivers automatically to the same NFE row |
| 42 | Attendance in another round: normal save is blocked before HTTP and preserves NFE data |
| 43 | Attendance in another round: correction delivers automatically to the same NFE row |
| 44 | Registration centre/partner mismatch: normal save is blocked before HTTP and preserves NFE data |
| 45 | Registration centre/partner mismatch: correction delivers automatically to the same NFE row |
| 46 | Education service round mismatch: normal save is blocked before HTTP and preserves NFE data |
| 47 | Education service round mismatch: correction delivers automatically to the same NFE row |
| 48 | Receiver down: source form still saves and target remains unchanged with a durable retry |
| 49 | Receiver restart automatically delivers the same failed event without manual resubmission |
| 50 | NFE storage unavailable: complete child/photo event rolls back and no unnecessary image bytes upload |
| 51 | NFE storage recovery commits the same event and preserves the correct photo |
| 52 | Browser 200-photo import: all 200 children, registrations, image checksums and references are correct |
| 53 | Photo uploads stay within the configured four concurrent upload lanes |
| 54 | Repeating all 200 photos uploads zero image bytes, keeps paths/IDs and creates no duplicates |
| 55 | Real receiver HTTP refuses missing and invalid service credentials |
| 56 | Twenty concurrent retries of one real event return the same ID without rewriting the registration |
| 57 | An applied event ID cannot be reused for another record |
| 58 | Twenty concurrent new events for one identity create one NFE record |
| 59 | Older updates and older deletions cannot overwrite a newer received value |
| 60 | A deletion tombstone prevents an older event from resurrecting the record |
| 61 | A missing-parent event remains retryable and the same event applies after the parent arrives |
| 62 | Receiver rejects cross-partner registration HTTP and rolls back its embedded child changes |
| 63 | Receiver independently rejects cross-partner attendance HTTP and preserves the whole existing day |
| 64 | Invalid multipart checksum rolls back child/registration metadata and preserves the previous photo |
| 65 | Deleting an attendance row republishes the day and removes the target row atomically |
| 66 | Deleting a disposable referral removes only that BMA identity and keeps the other referral |
| 67 | Deleting one registration preserves the shared child, remaining registration and its photo |
| 68 | Normal ProgramStaff deletion removes only its source type and preserves a legacy teacher with the identical BMA ID |
| 69 | Partner-assigned operator sees only its partner and can use masters without round permission |
| 70 | Restricted operator with ProgramStaff permission completes a real partner-scoped bulk sync |
| 71 | Forging another partner in a valid operator form cannot create a sync request |
| 72 | Restricted operator cannot read another operator/partner bulk-run audit |
| 73 | Bulk requests without a CSRF token are rejected |
| 74 | Source photo metadata unavailable: source save commits, delivery retries, and NFE data is untouched |
| 75 | Source photo storage recovery sends the same event and reuses the unchanged target image |
| 76 | Missing target image triggers exactly one necessary upload and repairs the photo on the same child |
| 77 | ProgramStaff import/model centre move updates one existing NFE teacher instead of duplicating it |
| 78 | Moving ProgramStaff back preserves the same NFE teacher identity |
| 79 | Embedded child: every common received field matches Compiler and NFE |
| 80 | Final audit: one target row per identity and no unresolved source events for the tested entities |
| 81 | Invalid ProgramStaff form creates neither a source row, outbox event nor target data |
| 82 | Normal staff form preserves an exact 200-character Arabic name and an email longer than 100 characters |
| 83 | A 201-character staff name is rejected before creating an event or truncating target data |
| 84 | Changing the UNICEF ID keeps the same child BMA identity and existing photo |
| 85 | Conflicting Student photo links block the complete event rather than copying another image |
| 86 | Correcting the Student link retries the original event and reuses the same child with its correct image |

## Runs

- all_scoped: `51c7a8fc-91c6-4089-8fcd-c5d4dd5daa83`
- photo_batch_browser: `fd43a11a-5ac5-4556-b7d8-04142736a98f`
- photo_batch_repeat: `cf26fb42-10f4-4920-a3e2-84b7b59a0b91`

## Portal follow-up completed

The final NFE teacher form/search correction and direct-access restrictions are now saved in the original repository. A further 51 focused end-to-end checks passed, and the current combined regression suites passed 338 tests. See [the completed portal validation report](teacher_portal_validation_2026-10-27.md). The previous usage-limit block is resolved.

## Deployment boundary

These results establish local application behavior for the existing contract. Production Azure networking/authentication,
the actual VM file-share mount/permissions/persistence, deployment migrations and running worker versions must receive a smoke test
in SIT after deployment. The local file-storage fault tests do not verify the VM mount. Compiler Azure storage configuration was unchanged.

Deploy NFE and apply migrations before Compiler, then restart the web and Celery/beat processes.

![Completed 200-photo import](images/manual-sync-200-photos.png)

[Machine-readable results](manual_sync_validation_2026-10-27.json)
