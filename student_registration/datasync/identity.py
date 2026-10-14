"""BMA identifiers are external keys, never local database primary keys."""


class UnresolvedDependency(Exception):
    """A referenced BMA record must arrive before this event can be applied."""


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
