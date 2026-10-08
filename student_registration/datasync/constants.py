# -*- coding: utf-8 -*-
"""Shared vocabulary for the Compiler -> BMA-NFE replication channel.

This module is deliberately dependency free and is kept byte-for-byte
identical in the Compiler repository (``student_registration/datasync/
constants.py``). Both sides of the integration import it so that the
resource names, operations and ordering rules can never drift apart.
"""

from __future__ import unicode_literals

#: Identifier the Compiler sends in every envelope it pushes.
SOURCE_SYSTEM_COMPILER = 'compiler'

#: Version of the wire contract. Bumped when the payload shape changes in a
#: way that older peers cannot understand.
CONTRACT_VERSION = '1.0'

RESOURCE_ROUND = 'mscc.round'
RESOURCE_CENTER = 'locations.center'
RESOURCE_TEACHER = 'mscc.teacher'
RESOURCE_REGISTRATION = 'mscc.registration'
RESOURCE_EDUCATION_SERVICE = 'mscc.education_service'
RESOURCE_GRADING = 'mscc.education_grading'
RESOURCE_REFERRAL = 'mscc.referral'
RESOURCE_ATTENDANCE = 'attendances.mscc_attendance'

#: Child records travel embedded in their registration, but they still get a
#: mapping row of their own so attendance rows can be resolved against them.
RESOURCE_CHILD = 'child.child'

#: Resources are applied in this order inside a batch. A registration can only
#: be written once its centre exists, an education service only once its
#: registration exists, and so on.
RESOURCE_ORDER = [
    RESOURCE_ROUND,
    RESOURCE_CENTER,
    RESOURCE_TEACHER,
    RESOURCE_REGISTRATION,
    RESOURCE_EDUCATION_SERVICE,
    RESOURCE_GRADING,
    RESOURCE_REFERRAL,
    RESOURCE_ATTENDANCE,
]

#: Human readable labels, used by the Django admin on both sides.
RESOURCE_LABELS = (
    (RESOURCE_ROUND, 'Round'),
    (RESOURCE_CENTER, 'Center'),
    (RESOURCE_TEACHER, 'Teacher'),
    (RESOURCE_REGISTRATION, 'Registration'),
    (RESOURCE_EDUCATION_SERVICE, 'Child education situation'),
    (RESOURCE_GRADING, 'Grading'),
    (RESOURCE_REFERRAL, 'Referral'),
    (RESOURCE_ATTENDANCE, 'Attendance'),
    (RESOURCE_CHILD, 'Child'),
)

OPERATION_UPSERT = 'upsert'
OPERATION_DELETE = 'delete'
OPERATIONS = (
    (OPERATION_UPSERT, 'Create or update'),
    (OPERATION_DELETE, 'Delete'),
)

#: Per-event outcomes reported back to the Compiler.
STATUS_APPLIED = 'applied'
STATUS_SKIPPED = 'skipped'
STATUS_FAILED = 'failed'


def resource_sort_key(resource):
    """Return the dependency rank of ``resource``.

    Unknown resources sort last so that a peer running a newer contract
    cannot push an unrecognised resource ahead of the records it depends on.

    Args:
        resource (str): One of the ``RESOURCE_*`` values.

    Returns:
        int: Index into :data:`RESOURCE_ORDER`, or its length when unknown.
    """
    try:
        return RESOURCE_ORDER.index(resource)
    except ValueError:
        return len(RESOURCE_ORDER)
