# Sync verification

The integration uses one event pipeline for Compiler records, embedded child
metadata and available profile photos. Registration metadata and its photo
reference are acknowledged only after the complete receiver transaction succeeds.

## Verified behavior

Regression checks use isolated PostgreSQL, generated images and test storage.

The saved implementation passes 161 combined sync/transport/concurrency tests
and seven existing Compiler outbox delivery tests. A local HTTP exercise also
transferred four initial photos, reused them without another source image read,
repaired an in-place destination edit, restored a deleted file and displayed the
saved image. A batch of 200 repeated registration updates completed in 33.69
seconds with zero uploaded image bytes, zero source image reads and a peak of
four concurrent requests. These timings use local files and localhost services;
they are not deployed Azure throughput measurements.

- BMA IDs resolve existing records and prevent duplicate child/registration rows.
- Dependency ordering covers rounds, centers, registrations, education services,
  assessments, grading, referrals and child attendance rows.
- Profile photos are transferred as validated image bytes in the registration
  request. Invalid images and checksums are rejected.
- Failed image writes roll back metadata and leave the event retryable. Retry,
  duplicate delivery and stale-event protection preserve the latest valid data.
- Image replacement, clearing, unchanged-image reuse and retained previous files
  are covered by the regression suite.
- Local NFE image and embedded-child metadata edits are audited when overwritten.
  Duplicate acknowledgements retain the original local ID and overwrite result.
- The source admin shows newest events first, separate queued/delivered local
  timestamps, explicit Yes/No overwrite text and the receiver's result.
- Timestamp handling is verified with both timezone-aware and naive database
  settings.
- Known photo versions avoid source image reads and file uploads when NFE's
  current copy verifies correctly. Missing/edited images request bytes and are
  repaired within the same event and delivery attempt.
- Transport checks exercise actual TCP keep-alive; concurrency checks use
  independent PostgreSQL connections for slot, event and child exclusion.

## Storage configuration

Compiler's existing Azure media storage configuration is unchanged. The sender
opens the linked Student image through its existing field storage.

NFE defaults to a mounted VM file share for media and generated exports.
`/mnt/nfe-media` is a deployment placeholder, with comments identifying where
it must be changed. The storage backend rejects missing mounts and media paths
outside the configured share. It does not select Azure from legacy credentials.

Automated storage checks cover missing mounts, prevention of local fallback
directories, mounted-share writes, share recovery and export round trips.
Tests simulate a mount using temporary storage; they do not establish an actual
connection to the provided VM or migrate existing cloud files.

## Deployment verification

Apply receiver migrations, configure the real mount and run as the deployed
application service identity:

```sh
python manage.py migrate
python manage.py datasync_photo_storage_check --require-share --write-test
```

Then synchronize a known child, confirm the database reference and physical file
on the share, and test share-outage recovery. Follow NFE's
`docs/file_share_storage.md` for deployment paths and container mounts.

The regression suite uses disposable PostgreSQL, generated images and temporary
storage. Live Azure access and the supplied VM/share configuration remain checks
for the deployment environment.
