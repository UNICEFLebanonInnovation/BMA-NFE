# MEHE Linux deployment and local Compiler test

This deployment runs NFE on app VM **172.16.2.101**, connects to PostgreSQL on
**192.168.41.30**, and stores uploaded photos/exports on the actual mounted share
from **192.168.41.31**. It uses `config.settings.mehe` and the standalone
`compose.mehe.yml`; do not combine it with the legacy `production.yml`.

## Inputs that must be filled onsite

Copy `env.mehe.example` to `.env.mehe` on the app VM. It is ignored by Git and
Docker builds. The known VM IPs and app-side paths are already supplied. Fill:

- The PostgreSQL database name, application username and password. Confirm its
  port and TLS policy (`MEHE_DB_SSLMODE`). The database must already exist and
  allow connections from the app VM.
- A fresh `DJANGO_SECRET_KEY` of at least 50 characters, e.g. generated with
  Python's `secrets.token_urlsafe(64)`.
- The actual SMB share name/NFS export path, its mount credentials/service
  identity and the app-host mount path. The IP alone is not a share path.
- The HTTPS certificate/private-key files. The certificate must cover the chosen
  host. For the supplied IP URL it must include IP SAN `172.16.2.101`. If MEHE
  supplies a DNS hostname, update `MEHE_HOST`, `DJANGO_ALLOWED_HOSTS`,
  `DJANGO_CSRF_TRUSTED_ORIGINS` and the local Compiler URL together.

No database password, API token, share password or certificate private key is
stored in the tracked templates. The host needs Docker Engine/Compose v2,
`mountpoint` (util-linux), `openssl`, and the appropriate SMB/NFS client tools.

## Mount the real share first

The application service account must be able to read/write the supplied remote
share. Mount it on the app VM using MEHE's protocol, share path and credentials;
the example host path is `/mnt/nfe-media`. Set `NFE_FILE_SHARE_HOST_PATH` to that
actual mount root. Configure the OS to restore the mount on reboot.

The app, export workers and Nginx all see that share as `/mnt/nfe-media`.
The MEHE profile checks Linux mount metadata for SMB/NFS and verifies the
configured server. It refuses an ordinary local bind directory or a share from a
different server, including on container restart. A missing mount never becomes
a substitute local media directory.

## Build or transfer the image

Build from this NFE checkout on the development machine:

```sh
docker build --platform linux/amd64 -f compose/django/Dockerfile -t bma-nfe:mehe .
```

The deployment intentionally uses the already loaded app image. For an onsite
host without registry access, transfer it with `docker save` / `docker load`:

```sh
docker save -o bma-nfe-mehe.tar bma-nfe:mehe
# On the app VM:
docker load -i bma-nfe-mehe.tar
```

The Compose stack also needs `redis:7.4-alpine` and `nginx:stable-alpine`. Pull
them on the app VM, or transfer the tested images with the same save/load method.
Only Nginx HTTPS is published. PostgreSQL remains on the separate database VM;
Redis and the app's Gunicorn port are internal to the Compose network.

## Prepare and start NFE

From the NFE checkout on the app VM:

```sh
sh compose/mehe/deploy.sh preflight
sh compose/mehe/deploy.sh prepare
sh compose/mehe/deploy.sh up
sh compose/mehe/deploy.sh status
```

`prepare` applies migrations to the configured NFE database, collects static
assets and performs a temporary photo write/read/delete. For an existing
installation, use its normal database backup/change procedure before migration.
The preflight does not print credentials. Internal deployments intentionally do
not request browser HSTS preload or force HSTS onto unrelated subdomains;
`check --deploy` may report those optional HSTS warnings.

The stack runs web, the default Celery worker, a dedicated `mscc_export` worker,
the scheduler, Redis and Nginx. Startup verifies the external DB and the real
share. Nginx waits for the app readiness check. Container restart policies handle
process failures; keep the OS file-share mount configured persistently.

Create the administrator and the local Compiler's dedicated API account:

```sh
sh compose/mehe/deploy.sh admin
sh compose/mehe/deploy.sh token
```

The token command prints the service token to your terminal. Put that value in
the local Compiler's ignored `.env.mehe-local`, never in Git. The service cannot
log into the UI and is separate from the administrator. Repeating the command
reuses its token. It refuses to repurpose an existing human/staff account.

## Configure the local Compiler

Use Compiler's `env.mehe-local.example` and `docs/mehe_local.md`. Its dedicated
`config.settings.mehe_local` profile reads the MEHE endpoint/token independently
of the temporary staging literals in the ordinary base settings. A supplied
internal CA bundle is used for both metadata and photo requests; certificate
verification stays enabled. Web, sync worker and scheduler use the same profile.

The local computer must be onsite/on the approved network and able to reach the
app VM's HTTPS port. It does not need direct DB or file-share access for sync.
The local source database remains local; NFE performs remote DB/share writes.

## Verify the actual deployment

```sh
docker compose --env-file .env.mehe -f compose.mehe.yml exec django python manage.py datasync_photo_storage_check --require-share --write-test
```

Run the local Compiler's `check`, start it, and use its Bulk sync page. Select
only the synthetic partner/round. Confirm all events are Sent, open the child
photos in NFE, and verify the files on the actual remote share. Repeat without
changing anything: IDs/file names must stay stable and unchanged photos must not
be uploaded again. Then test a replacement and a clear. Use an isolated test
installation for outage/read-only checks.

Photos are fetched through the authenticated `/media/` route. It applies
MEHE/partner/centre or Django admin child-view permissions before Nginx reads
the file through an internal-only location. Anonymous users, unrelated partners,
the replication service and URLs for unreferenced retained photos are denied.
Static assets are served separately. Old files remain retained after a reference
is replaced/cleared; they are not current child photos.

Code/configuration validation cannot verify credentials, routing, mount rights or
certificates on the real VMs until these checks run onsite.
