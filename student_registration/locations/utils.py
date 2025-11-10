# -- coding: utf-8 --
from itertools import chain
import datetime

from django.db.models import Exists, OuterRef
from import_export import resources, fields


def to_array(fields, obj):
    data = {}
    for field_name in fields:
        if hasattr(obj, field_name):
            data[field_name] = getattr(obj, field_name)

    return data


