# Photo transfer efficiency

The same registration event and `/api/sync/events/` endpoint handle records and
photos. Compiler's Azure storage configuration is unchanged.

## Transfer decisions

Compiler stores a recomputable SHA-256 fingerprint of each Student photo version
in `SourcePhotoFingerprint`. The key includes the storage reference, storage
modification time when available, and the Student's modification time. Blob
metadata may still be requested, but unchanged image
bytes need not be downloaded again. Writes outside Django on a backend lacking
modification metadata require a Student save to invalidate its fingerprint.
If only Student metadata changes, the image is rehashed; an unchanged checksum
still avoids transferring image bytes to NFE.

- First encounter or changed source version: read and upload the photo with its
  registration. The image is bounded by the configured photo size limit.
- Known source version: send registration metadata and `photo_sync.action=verify`
  with its checksum, without attaching a file.
- NFE locks the child and verifies its actual stored image bytes, image format,
  limits and checksum within the event transaction. Matching images are reused.
- A missing, locally edited or corrupted NFE photo requests an upload. Metadata
  is rolled back. Compiler immediately continues the **same event ID and delivery
  attempt** with image bytes attached. NFE then commits records and photo reference
  together. Negotiation does not create a failed event log or a second sync engine.
- If the share cannot be read, the event is deferred without downloading and
  uploading another image unnecessarily.

The sender checks receiver capabilities before using verification. An older
receiver without `verified_reuse` continues receiving normal multipart uploads.
Duplicate acknowledged events remain safe, including after a lost HTTP response.

## Connections and concurrency

HTTP requests use Requests Sessions and connection pooling. Single-save tasks
reuse a pool local to their process/thread. Bulk delivery creates independent
worker lanes, each reusing its own Session for multiple events and closing it
on completion. Sessions are not shared between simultaneous threads.

Dependency stages complete in order: rounds, centers and teachers precede
registrations, which precede their dependent education and attendance data.
Registration events within a stage can run in parallel.

PostgreSQL advisory locks provide a shared slot limit across Compiler workers,
exclude duplicate event deliveries and serialize events affecting the same child.
Busy events remain pending for a later sweep without consuming a delivery attempt.
Locks are released on completion/error or when the worker database connection
closes. Workers must use direct PostgreSQL connections or session pooling and
the same concurrency setting; transaction pooling is not suitable for these locks.

```dotenv
# Compiler sync worker settings; no Azure storage setting changes.
DATASYNC_PHOTO_REUSE_ENABLED=True
DATASYNC_PARALLEL_UPLOADS=4
```

The concurrency value is constrained to 1–16. Use 1 for sequential delivery.
Changing it requires restarting all Compiler web/worker processes so their shared
slot limit agrees. Receiver capacity and network throughput still determine speed.

## Deployment and verification

Deploy the updated NFE receiver first, then apply Compiler's new fingerprint
migration before starting the updated sender:

```sh
python manage.py migrate
```

NFE's existing file-share requirements and media-serving configuration still
apply. Existing files are not migrated or deleted by this optimization.

Verify an initial photo transfer, an unchanged registration update without a file
upload, a source photo replacement, and repair after a local NFE photo edit or
deleted file. Check retries after a share outage and duplicate event delivery.
Concurrency tests use independent PostgreSQL connections; transport tests verify
TCP connection reuse. Measure throughput with representative images in SIT before
choosing a higher concurrency limit. Local tests do not benchmark deployed Azure.
