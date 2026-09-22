# -*- coding: utf-8 -*-
"""The endpoint the Compiler pushes MSCC changes to."""

from __future__ import unicode_literals, absolute_import, division

import logging

from django.conf import settings
from rest_framework import status
from rest_framework.authentication import (
    SessionAuthentication,
    TokenAuthentication,
)
from rest_framework.response import Response
from rest_framework.views import APIView

from .constants import CONTRACT_VERSION, RESOURCE_ORDER, SOURCE_SYSTEM_COMPILER
from .permissions import IsSyncClient
from .services import EnvelopeError, ingest_events

logger = logging.getLogger(__name__)


def _allowed_source_systems():
    """Return the producers this instance accepts data from."""
    return getattr(
        settings, 'DATASYNC_ALLOWED_SOURCE_SYSTEMS', [SOURCE_SYSTEM_COMPILER]
    )


def _max_batch_size():
    """Return the largest batch this instance will accept in one request."""
    return getattr(settings, 'DATASYNC_MAX_BATCH_SIZE', 200)


class SyncIngestView(APIView):
    """Accept a batch of MSCC change events from an upstream system.

    ``POST`` body::

        {
          "source_system": "compiler",
          "contract_version": "1.0",
          "events": [
            {
              "event_id": "<uuid4>",
              "resource": "mscc.registration",
              "operation": "upsert",
              "source_id": 1234,
              "source_modified": "2026-08-30T09:15:00Z",
              "payload": {...}
            }
          ]
        }

    The response reports the outcome of every event separately. A ``failed``
    entry carrying ``"retryable": true`` means a parent record had not been
    replicated yet and the producer should send the event again.
    """

    authentication_classes = (TokenAuthentication, SessionAuthentication)
    permission_classes = (IsSyncClient,)

    def get(self, request):
        """Report what this instance accepts, for connectivity checks."""
        return Response({
            'contract_version': CONTRACT_VERSION,
            'enabled': getattr(settings, 'DATASYNC_INGEST_ENABLED', True),
            'resources': RESOURCE_ORDER,
            'max_batch_size': _max_batch_size(),
            'allowed_source_systems': _allowed_source_systems(),
        })

    def post(self, request):
        """Apply a batch of events and return a per-event outcome."""
        if not getattr(settings, 'DATASYNC_INGEST_ENABLED', True):
            return Response(
                {'detail': 'Replication ingest is disabled on this instance.'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        body = request.data if isinstance(request.data, dict) else {}
        source_system = body.get('source_system') or SOURCE_SYSTEM_COMPILER
        if source_system not in _allowed_source_systems():
            return Response(
                {'detail': 'Unknown source system "{}".'.format(source_system)},
                status=status.HTTP_403_FORBIDDEN,
            )

        events = body.get('events')
        if not isinstance(events, list):
            return Response(
                {'detail': '"events" must be a list.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if len(events) > _max_batch_size():
            return Response(
                {
                    'detail': 'Batch too large: {} events, maximum is {}.'.format(
                        len(events), _max_batch_size()
                    )
                },
                status=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            )

        try:
            outcome = ingest_events(events, source_system)
        except EnvelopeError as error:
            return Response({'detail': str(error)}, status=status.HTTP_400_BAD_REQUEST)

        logger.info(
            'datasync: %s applied, %s skipped, %s failed from %s',
            outcome['applied'], outcome['skipped'], outcome['failed'], source_system,
        )
        outcome['source_system'] = source_system
        outcome['contract_version'] = CONTRACT_VERSION
        return Response(outcome, status=status.HTTP_200_OK)
