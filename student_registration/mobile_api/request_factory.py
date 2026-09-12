# -*- coding: utf-8 -*-
"""Build Django ``HttpRequest`` objects from JSON payloads.

The web platform's forms save data straight from ``request.POST`` (and read
``request.user`` / ``request.session`` / ``messages``). Re-using those forms
from the API guarantees byte-for-byte parity with the website, so the mobile
push handler wraps every payload in a request that looks exactly like a browser
submission.
"""
from __future__ import unicode_literals

import json

from django.contrib.messages import constants as message_constants
from django.contrib.messages.storage.base import BaseStorage
from django.http import QueryDict
from django.test import RequestFactory
from django.utils.datastructures import MultiValueDict


class MemoryMessageStorage(BaseStorage):
    """Message storage that keeps messages in memory (no cookies/session)."""

    def _get(self, *args, **kwargs):
        return [], True

    def _store(self, messages, response, *args, **kwargs):
        return []

    def collect(self):
        """Return the queued messages as ``(level, text)`` tuples."""
        return [(m.level, str(m.message)) for m in self._queued_messages]

    def warnings(self):
        return [
            text for level, text in self.collect()
            if level >= message_constants.WARNING
        ]


def to_querydict(data):
    """Convert a JSON object into a ``QueryDict`` the way a browser would post it.

    Lists become repeated keys (``getlist``), booleans become ``True``/``False``
    strings, dictionaries are JSON encoded and ``None`` values are dropped so
    that ``.get()`` returns ``None`` exactly as for an absent input.
    """
    qd = QueryDict(mutable=True)
    for key, value in (data or {}).items():
        if value is None:
            continue
        if isinstance(value, (list, tuple, set)):
            qd.setlist(key, [_to_str(v) for v in value if v is not None])
        else:
            qd[key] = _to_str(value)
    return qd


def _to_str(value):
    if isinstance(value, bool):
        return 'True' if value else 'False'
    if isinstance(value, dict):
        return json.dumps(value)
    return str(value)


def build_request(user, data=None, method='POST', path='/api/mobile/v1/push/', get_params=None):
    factory = RequestFactory()
    if method == 'POST':
        request = factory.post(path)
    else:
        request = factory.get(path, get_params or {})
    request.user = user
    request.POST = to_querydict(data)
    request._files = MultiValueDict()  # FILES is a read-only property
    request.session = {}
    request._messages = MemoryMessageStorage(request)
    return request
