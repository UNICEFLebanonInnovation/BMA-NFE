"""Verify Linux mount metadata without accepting an ordinary bind directory."""
from pathlib import Path
import os
import re
import socket

def _unescape(value):
    return re.sub(r'\\([0-7]{3})', lambda match: chr(int(match.group(1), 8)), value)

def remote_share_mount(root, expected_server):
    root = os.path.realpath(root)
    try:
        lines = Path('/proc/self/mountinfo').read_text().splitlines()
    except OSError as error:
        raise OSError('Linux mount metadata is unavailable') from error
    for line in reversed(lines):
        left, separator, right = line.partition(' - ')
        fields, filesystem = left.split(), right.split()
        if not separator or len(fields) < 5 or len(filesystem) < 2:
            continue
        if _unescape(fields[4]) != root:
            continue
        kind, source = filesystem[0], _unescape(filesystem[1])
        if kind not in ('cifs', 'nfs', 'nfs4'):
            raise OSError('NFE media must be a mounted SMB or NFS share')
        server = source[2:].split('/', 1)[0] if source.startswith('//') else source.split(':', 1)[0]
        if server != expected_server:
            try:
                addresses = {item[4][0] for item in socket.getaddrinfo(server, None)}
            except OSError as error:
                raise OSError('Cannot verify the file-share server') from error
            if expected_server not in addresses:
                raise OSError('NFE media is mounted from a different file-share server')
        return {'filesystem': kind, 'server': server}
    raise OSError('The configured file-share root is not a visible mount')
