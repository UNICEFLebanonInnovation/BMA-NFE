# BMA-NFE receiver sync QA - 26 October 2026

## Outcome

The earlier Compiler assessment, mapping and partner fixes work with the existing receiver contract. No new endpoint or database migration is needed for them. A separate receiver event-identity issue was reproduced, fixed and retested in the original BMA-NFE clone.

**140 receiver regression tests passed**, including 13 new event-identity tests. **13 live local integration checks passed**, including a 19-event all-category bulk run with zero unchanged photo bytes uploaded.

## Failure and fix

Before the fix, submitting a previously applied event UUID with a different source record ID returned `skipped` and the first record's local NFE ID. A caller could therefore mistake another record's receipt for successful delivery. A failed event's audit row could also be reassigned by a mismatched attempt.

An event UUID is now bound to the original **source system, resource, normalized source ID and operation**. A mismatch returns a per-event `failed` result with `retryable: false` and no local ID. It does not change business data or the original audit receipt. The same check runs after obtaining the database row lock, so two competing first deliveries cannot both claim the UUID. Late failure logging also preserves the existing identity.

Legitimate retries still return the original receipt. A failed event can retry with corrected data for the same identity. Payload bytes and timestamps are not treated as immutable identity fields: the Compiler rebuilds payloads from current records when retrying. One rejected event does not block unrelated events in the same batch.

Changed files: `student_registration/datasync/services.py` and `student_registration/datasync/tests/test_event_identity.py`.

## Validation

The 13 new regression tests were run against the old service first: 10 reproduced failures and three compatibility checks passed. After the fix, all 140 receiver sync tests passed. Tests cover applied, skipped and failed receipts; source/resource/operation mismatches; normalized IDs; rebuilt payloads; batch isolation; and competing database connections.

The following checks then used real HTTP requests, rendered source admin/application forms, the local Celery worker and independent database/file assertions:

1. Fresh source round saved through admin and delivered to updated NFE.
2. Reusing an applied event ID for another record, resource or operation is rejected and the original receipt stays unchanged.
3. Twenty concurrent legitimate retries return the original NFE ID without extra writes.
4. Two different records racing with one event ID produce one committed record and one rejected collision.
5. Failed event reserves its identity; correcting the same event payload retries successfully.
6. One identity collision does not block an unrelated valid event in the same batch.
7. Partner edit travels through existing embedded sync and updates the original receiver partner.
8. Teacher mapping changes reuse the existing teacher-centre identities without extra assignments.
9. Assessment with blank optional grades still reaches the same receiver record.
10. Two registrations share one photo upload; unchanged resave uploads zero image bytes.
11. All-category round bulk completes through the updated receiver with zero photo bytes.
12. Full local receiver audit has no duplicate BMA identities; teachers remain scoped by centre.
13. Both applications remain available and all source outbox events are Sent.

## Review fixtures

- Synthetic fixture label: `Receiver QA 360a86a`.
- New source round ID: `10`; NFE local round ID: `9`.
- Completed bulk request: `a0f6ccdd-854b-46dc-ad87-2a72e9c3afd6` (19 sent, none pending or failed).
- Shared-child photo replacement uploaded one image body for two registrations; unchanged resave uploaded zero bytes. The green test photo was restored.
- All source outbox events were Sent at completion. Deliberately malformed receiver requests remain audit entries; they do not represent undelivered source events.

## Scope and deployment

The current teacher identity remains **BMA ID + centre**. The mapping test reused the two existing centre assignments; this change does not convert teachers into a single global person model.

Both projects were tested locally using isolated PostgreSQL databases and test media directories. Compiler Azure storage settings and NFE file-share settings were unchanged. Azure/SIT connectivity and the actual VM file-share mount still need testing in that environment.

The changes are saved in the original `BMA-NFE` clone on `claude-api-connection`. No new migrations are required. No commits, pushes or deployments were performed.
