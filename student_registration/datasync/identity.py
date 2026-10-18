"""BMA identifiers are external keys, never local database primary keys."""


class UnresolvedDependency(Exception):
    """A referenced BMA record must arrive before this event can be applied."""


class StaleEvent(Exception):
    """An older event must not change a more recently synchronized record."""


def source_timestamp(value):
    """Read an optional timezone-aware ISO 8601 source modification time."""
    from django.utils.dateparse import parse_datetime
    from django.utils.timezone import is_naive

    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError('source_modified must be an ISO 8601 timestamp')
    timestamp = parse_datetime(value)
    if timestamp is None or is_naive(timestamp):
        raise ValueError('source_modified must include a timezone')
    from django.conf import settings
    from django.utils.timezone import get_default_timezone, make_naive
    if not settings.USE_TZ:
        # Match DateTimeField values returned by this project's database.
        timestamp = make_naive(timestamp, get_default_timezone())
    return timestamp


def normalize_bma_id(value):
    """Normalize integer/string IDs while rejecting missing or invalid keys."""
    if isinstance(value, bool) or not isinstance(value, (str, int)):
        raise ValueError('BMA ID must be a non-empty string or integer')
    value = str(value).strip()
    if not value or len(value) > 64:
        raise ValueError('BMA ID must contain between 1 and 64 characters')
    return value


def reference_bma_id(key):
    """Read a reference's source_id, accepting bma_id as an explicit alias."""
    if not isinstance(key, dict):
        return normalize_bma_id(key)
    source_id = key.get('source_id')
    bma_id = key.get('bma_id')
    if source_id is not None and bma_id is not None:
        if normalize_bma_id(source_id) != normalize_bma_id(bma_id):
            raise ValueError('source_id and bma_id refer to different BMA records')
    return normalize_bma_id(source_id if source_id is not None else bma_id)
