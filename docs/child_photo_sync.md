# One Compiler to NFE sync: records and child photos

The sync is enabled by default in the checked-out code. There is one outbox,
one dispatcher/worker pipeline, one API endpoint, and one completion status per
event. Available child photos are part of registration events.

```text
Compiler save
  -> SyncEvent in the outbox
  -> after commit: Celery worker
  -> prepare record + embedded child + available profile photo
  -> POST /api/sync/events/
  -> NFE resolves BMA IDs and saves record/child/photo reference together
  -> acknowledge complete event
  -> Compiler marks the same outbox event sent
```

Metadata-only requests use JSON. New/changed images use multipart with a JSON
`envelope` and the file in the same registration request. Known source image
versions first verify NFE's existing copy without an attachment. A missing or
edited NFE copy requests bytes; the same event immediately continues with its
file attached. Each request contains one registration, with a default shared
limit of four concurrent deliveries. Dependency stages remain ordered.
The former `/api/sync/photos/child/` route has been removed. Previously queued
`child.photo` jobs are converted to registration events in the same dispatcher;
new saves do not create photo-only jobs.

## 1. Initialize the environments once

Deploy the receiver first. On NFE:

1. Mount the MEHE file share inside the NFE server/container with read/write
   permissions for the application service identity. Configure its actual path.
2. Run `python manage.py migrate`.
3. Prepare nationalities and required lookup values. Configure round/partner
   associations used by the UI; those associations are not auto-replicated.
4. Run `python manage.py datasync_create_client` to provision the restricted
   service account/token. Supply that token to Compiler through its environment.
5. Verify image storage with the commands below. Keep existing authorized media
   serving rules so copied photos display through the child profile.

Example NFE environment for a mounted file share:

```dotenv
DATASYNC_INGEST_ENABLED=True
# DEPLOYMENT: CHANGE this placeholder to the provided VM file-share mount.
NFE_FILE_SHARE_ROOT=/mnt/nfe-media
NFE_MEDIA_STORAGE_BACKEND=student_registration.media_storage.VMFileShareStorage
```

`/mnt/nfe-media` is a placeholder. Change it during deployment to the actual mount. A Windows deployment
can use the approved UNC path accessible to its service. Creating a share does
not mount it or automatically configure Django to use it. All NFE instances
must see the same storage. The receiver defaults to mount-enforced file-share storage; generated exports use the same storage.

```text
python manage.py datasync_photo_storage_check
python manage.py datasync_photo_storage_check --require-share --write-test
```

The first command reports the actual backend/location. The second writes,
reads and removes a generated one-pixel image without changing a child. Successful
I/O alone does not prove the directory is the mounted MEHE share; confirm the
reported path with the hosting administrator.

On Compiler:

1. Run `python manage.py migrate`.
2. Configure the NFE endpoint/token. Keep the existing Azure storage settings unchanged.
3. Start the configured Celery worker and Celery Beat.

```dotenv
DATASYNC_ENABLED=True
DATASYNC_TARGET_URL=https://YOUR-NFE-HOST/api/sync/events/
DATASYNC_TARGET_TOKEN=YOUR-NFE-SERVICE-ACCOUNT-TOKEN
```

The sender reads photos through the existing Student image field's storage;
no Compiler storage configuration change is required. Do not place tokens or
storage keys in source control. No real target
URL/token was discovered in the local checkout environment files; they may
be supplied separately on the deployment server and must be verified there.
Setting defaults to enabled does not start a server/worker or deploy anything.
An explicit deployment environment value of False still disables its side.

The controls are `DATASYNC_ENABLED` on Compiler and `DATASYNC_INGEST_ENABLED`
on NFE. The old photo enablement names are compatibility aliases to these
same controls; there is no independent photo enablement requirement.

## 2. Initial import for existing records

Run on Compiler, first for a small staging sample:

```text
python manage.py datasync_backfill --dry-run --limit 5
python manage.py datasync_backfill --limit 5
```

The dry run reports resource counts and photo-link audit results. It writes no
outbox rows and transfers no data. The real command checks the target configuration and verifies that NFE
advertises the combined record/photo contract, then queues records in dependency order, and runs the normal dispatcher.
Registration events include their available child photos automatically.
After verifying the sample, omit `--limit 5` for the full initial import.
Use `--no-send` if the worker should deliver the queued events later.

Rounds and centers precede registrations; partners resolve through their BMA
references. Children are embedded in registrations. Education services,
assessments, grading, referrals and attendance follow their dependencies.
Teachers still require the correct school-to-center and round mapping.

`datasync_backfill_photos --dry-run --child-id 900` remains a focused read-only
link audit. Its non-dry mode now requeues normal registrations with their photos;
it is a troubleshooting convenience, not a second synchronization engine.
It is not required during a normal initial import.

## 3. Normal ongoing flow

At Django startup, Compiler's `DataSyncConfig.ready()` registers the save/delete
and relation-change signal handlers. A supported record save creates a durable
SyncEvent. Delivery is scheduled after the database transaction commits.
The worker reads current source data and constructs the event with its UUID,
resource, BMA source ID and source timestamp.

For a registration it uses:

```text
Registration.child_id -> synchronized Child identity
Registration.student_old -> Student.id -> Student.std_image -> source image
```

`std_image` contains a relative storage name such as `profiles/example.png`.
The worker fingerprints photo versions through existing Django storage using
Compiler's own Azure credentials. Cached versions avoid another image download
and upload when NFE verifies that its actual copy still matches. Blob metadata
may still be read to check for source changes. It does not pass public/signed
Azure URLs or storage keys to NFE.
The request carries a bounded image file, checksum and photo descriptor alongside
the registration and child data. Updating the linked Student's photo requeues
the same normal registration pipeline. No second button or photo request runs.

NFE authenticates the service account, validates the contract and event, resolves
BMA IDs to its own primary keys, and creates/updates the required records.
It verifies the image bytes, size, dimensions and SHA-256, saves the image into
Child.photo's configured storage, and updates the image reference in that same
event's database transaction. It records success only when the complete event
succeeds. Normal JSON fields cannot assign unverified photo paths.

Compiler marks the event sent only after NFE acknowledges it. Repeat deliveries
are skipped safely. A record/storage/network failure leaves the event failed
for retry; the receiver rolls back the event's database changes and attempts
cleanup of a newly written file. Previous valid files are retained. Filesystem
operations cannot participate atomically in SQL; failed cleanup may leave an
orphan for storage maintenance, without changing the committed child reference.

Celery Beat's existing sweep runs every 300 seconds by default. Retry backoff
starts at 60 seconds and increases, capped at one hour. The existing default
budget is 12 attempts; exhausted events are marked abandoned for operator review.
Photos are never uploaded inline in a partner's save request when the broker
is unavailable. New record saves and Student photo changes enter this same flow.

## Photo boundaries

A missing Student link is reported in the event detail and preserves any
existing NFE photo while the record syncs. Conflicting links or a missing linked
Student require correction. Verify one known child/Student pair before go-live.
The source file is read at delivery; changes made outside Django save paths
need a normal backfill to be detected.

JPEG, PNG and WebP are accepted (default 5 MiB, 20 million pixels). Unchanged
images do not create another destination file. An explicitly cleared photo
clears only a photo previously managed by sync. Previous files remain subject
to the storage operator's retention policy. This covers child profile photos;
teacher files and identity/birth/UNHCR scans are not added to this scope.

See `docs/sync_photo_performance.md` for fingerprint caching, verified reuse,
connection pooling, the PostgreSQL concurrency guards and deployment settings.

## Staging verification

Verify a registration with a known linked Student/photo, its display in NFE,
and the physical destination path in the real share. Stop the share/NFE during
an update: the entire event must remain retryable and its previous data/photo
must stay intact. Restore access and replay the same event successfully. Also
check duplicate delivery, older events, missing links and explicit photo clearing.

Run `python manage.py test student_registration.datasync` in each project's
staging test environment. Local tests use generated images, temporary file
storage and disposable PostgreSQL; they do not verify live Azure, the real MEHE
mount, separate Compiler database models or deployed Celery/network transport.
