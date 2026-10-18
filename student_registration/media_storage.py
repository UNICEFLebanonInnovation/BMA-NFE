"""Shared media storage on the mounted file share provided for NFE."""
import os

from django.conf import settings
from django.core.files.storage import FileSystemStorage


class FileShareUnavailable(OSError):
    """The configured share is absent; local fallback writes are refused."""


class VMFileShareStorage(FileSystemStorage):
    def __init__(self, *args, share_root=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.share_root = share_root or getattr(settings, 'NFE_FILE_SHARE_ROOT', self.location)

    def check_available(self):
        root = self.share_root
        if not os.path.isabs(root) or not os.path.isdir(root) or not os.path.ismount(root):
            raise FileShareUnavailable('The configured NFE file-share mount is unavailable')
        root = os.path.realpath(root)
        location = os.path.realpath(self.location)
        try:
            inside_share = os.path.commonpath([root, location]) == root
        except ValueError:
            inside_share = False
        if not inside_share:
            raise FileShareUnavailable('NFE media storage must be inside its file-share mount')

    def path(self, name):
        # Check before FileSystemStorage can create directories on local disk.
        self.check_available()
        return super().path(name)
