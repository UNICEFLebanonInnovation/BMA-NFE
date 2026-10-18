# NFE file-share storage

Uploaded files, synchronized child photos and generated exports use NFE's default
Django storage. The production default is `VMFileShareStorage`, backed by the
mounted share supplied for the NFE VM. It rejects file operations when the mount
is missing. It does not create the mount or fall back to local disk or Azure.

## Deployment path

`/mnt/nfe-media` is a **placeholder**. Change the clearly marked deployment
setting in `config/settings/base.py`, or configure the server environment:

```dotenv
# CHANGE to the actual mounted share on the provided VM.
NFE_FILE_SHARE_ROOT=/mnt/nfe-media
NFE_MEDIA_STORAGE_BACKEND=student_registration.media_storage.VMFileShareStorage
```

The path must be an existing filesystem mount point visible to the application.
Mount SMB/NFS or the provided filesystem using the hosting team's instructions
before starting the app. The application service account needs read/write access.
For a Windows VM, use the approved UNC share root accessible to that account.

`MEDIA_ROOT` defaults to `NFE_FILE_SHARE_ROOT`. If media belongs in a subdirectory,
set `MEDIA_ROOT` to a path inside that mount and keep `NFE_FILE_SHARE_ROOT` at the
mount root. All web and worker instances must resolve the same files.

New files are stored as:

```text
<MEDIA_ROOT>/child_photos/sync/<child-key>/<event-id>.jpg
<MEDIA_ROOT>/export/<export-filename>
```

PNG and WebP photos keep their validated extensions. `Child.photo` contains the
relative storage name; image bytes are stored on the share. Replacement updates
the database reference and retains previous files for the storage retention policy.
The configuration does not migrate existing files from another storage system.

## Fetching photos

Templates use `Child.photo.url`, which resolves to NFE's own `/media/` URL with
the relative storage name. The browser fetches the NFE copy; NFE does not read
Azure again to display it. Compiler continues using its existing Azure storage.

In production Django does not automatically serve `/media/`. Configure the
deployment's media web server to read the same `MEDIA_ROOT`, preserving its
existing access controls. A separate web-server container must also mount the
share. The Compose override below mounts application services only; it does not
configure the media web server. After deployment, verify an authorized request
to a synchronized child's photo URL returns the expected image.

## Containers

The optional `compose.file-share.yml` override mounts the share into NFE's web
and worker services. Set `NFE_FILE_SHARE_HOST_PATH` to the actual host mount:

```dotenv
# CHANGE this host path during deployment.
NFE_FILE_SHARE_HOST_PATH=/mnt/nfe-media
```

Use the override together with the deployment's reviewed base configuration:

```sh
docker compose -f production.yml -f compose.file-share.yml config --quiet
```

The container path stays `/mnt/nfe-media`; the host path may differ. Missing
host directories are not automatically created. The legacy `production.yml`
still requires the deployment-specific database, process, domain and TLS setup
described in the deployment guide. This storage override does not replace it.
Keep the deployment's existing access controls when configuring media serving.

## Verify on the VM

Run with the deployed settings and application service identity:

```sh
python manage.py datasync_photo_storage_check --require-share --write-test
```

The command verifies mount enforcement and writes, reads and removes a temporary
image. It does not change child data. Then synchronize a test child and confirm
its relative `Child.photo` path resolves to a real file under the mounted share.
A mount/storage outage leaves the complete sync event retryable; the receiver
does not commit the new registration metadata or photo reference.

The placeholder and automated mount simulations do not verify the actual VM.
Confirm the real share source, path and permissions during deployment.

## Local development

An isolated local environment can explicitly select ordinary filesystem storage:

```dotenv
NFE_MEDIA_STORAGE_BACKEND=django.core.files.storage.FileSystemStorage
MEDIA_ROOT=/absolute/path/to/local-test-media
```

Use `--require-share` for deployment verification so this local override cannot
be mistaken for a mounted-share configuration.
