"""Choose where uploaded files (photographs, consent documents) are stored.

Deployments differ: the ministry hosts the application on its own servers
and keeps uploads on a local SFTP server, while other deployments use
Azure Blob Storage. Development machines keep files on disk. The choice is
made from environment variables, explicitly through ``MEDIA_STORAGE_BACKEND``
or otherwise from whichever credentials are configured.
"""

import base64
import binascii

FILESYSTEM = 'filesystem'
AZURE = 'azure'
SFTP = 'sftp'
BACKENDS = (FILESYSTEM, AZURE, SFTP)


def azure_key_is_valid(account_key):
    """Only a real base64 account key selects Azure, like the export storage."""
    if not account_key:
        return False
    try:
        base64.b64decode(account_key, validate=True)
    except (binascii.Error, ValueError):
        return False
    return True


def sftp_params(username='', password='', key_file='', port=None, timeout=None):
    """Build the paramiko ``connect`` arguments for the SFTP backend."""
    params = {}
    if username:
        params['username'] = username
    if password:
        params['password'] = password
    if key_file:
        params['key_filename'] = key_file
    if port:
        params['port'] = int(port)
    if timeout:
        params['timeout'] = int(timeout)
    return params


def select_backend(explicit='', sftp_host='', azure_account_key=''):
    """Return the backend name for the configuration at hand."""
    explicit = (explicit or '').strip().lower()
    if explicit:
        if explicit not in BACKENDS:
            raise ValueError(
                'MEDIA_STORAGE_BACKEND must be one of {}, not {!r}.'.format(
                    ', '.join(BACKENDS), explicit,
                )
            )
        return explicit
    if sftp_host:
        return SFTP
    if azure_key_is_valid(azure_account_key):
        return AZURE
    return FILESYSTEM


def media_storage(backend, *, sftp_host='', sftp_root='', sftp_connect=None,
                  sftp_known_host_file=None, azure_container='', azure_url_expiry=3600):
    """Return the ``STORAGES['default']`` entry for the chosen backend."""
    if backend == SFTP:
        if not sftp_host:
            raise ValueError('SFTP_STORAGE_HOST is required for the sftp media backend.')
        options = {
            'host': sftp_host,
            'params': dict(sftp_connect or {}),
            'root_path': sftp_root or '',
            'interactive': False,
        }
        if sftp_known_host_file:
            options['known_host_file'] = sftp_known_host_file
        return {'BACKEND': 'storages.backends.sftpstorage.SFTPStorage', 'OPTIONS': options}
    if backend == AZURE:
        return {
            'BACKEND': 'storages.backends.azure_storage.AzureStorage',
            'OPTIONS': {
                'azure_container': azure_container,
                'expiration_secs': azure_url_expiry,
            },
        }
    if backend == FILESYSTEM:
        return {'BACKEND': 'django.core.files.storage.FileSystemStorage'}
    raise ValueError('Unknown media storage backend {!r}.'.format(backend))
