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

# Reference data and the records everything else hangs off.
RESOURCE_ROUND = 'mscc.round'
RESOURCE_PACKAGE = 'mscc.package'
RESOURCE_CENTER = 'locations.center'
RESOURCE_TEACHER = 'mscc.teacher'
RESOURCE_REGISTRATION = 'mscc.registration'

# Per-child records, each pointing at a registration.
RESOURCE_EDUCATION_SERVICE = 'mscc.education_service'
RESOURCE_EDUCATION_RS_SERVICE = 'mscc.education_rs_service'
RESOURCE_EDUCATION_ASSESSMENT = 'mscc.education_assessment'
RESOURCE_GRADING = 'mscc.education_grading'
RESOURCE_REFERRAL = 'mscc.referral'
RESOURCE_PSS_SERVICE = 'mscc.pss_service'
RESOURCE_INCLUSION_SERVICE = 'mscc.inclusion_service'
RESOURCE_DIGITAL_SERVICE = 'mscc.digital_service'
RESOURCE_HEALTH_NUTRITION_SERVICE = 'mscc.health_nutrition_service'
RESOURCE_HEALTH_NUTRITION_REFERRAL = 'mscc.health_nutrition_referral'
RESOURCE_YOUTH_KIT_SERVICE = 'mscc.youth_kit_service'
RESOURCE_YOUTH_SERVICE = 'mscc.youth_service'
RESOURCE_YOUTH_ASSESSMENT = 'mscc.youth_assessment'
RESOURCE_YOUTH_REFERRAL = 'mscc.youth_referral'
RESOURCE_FOLLOW_UP_SERVICE = 'mscc.follow_up_service'
RESOURCE_RECREATIONAL = 'mscc.recreational'
RESOURCE_LEGO_SERVICE = 'mscc.lego_service'
RESOURCE_ATTENDANCE = 'attendances.mscc_attendance'

#: Child records travel embedded in their registration, but they still get a
#: mapping row of their own so attendance rows can be resolved against them.
RESOURCE_CHILD = 'child.child'

#: Resources are applied in this order inside a batch. A registration can only
#: be written once its centre exists, a service only once its registration
#: exists, and so on.
RESOURCE_ORDER = [
    RESOURCE_ROUND,
    RESOURCE_PACKAGE,
    RESOURCE_CENTER,
    RESOURCE_TEACHER,
    RESOURCE_REGISTRATION,
    RESOURCE_EDUCATION_SERVICE,
    RESOURCE_EDUCATION_RS_SERVICE,
    RESOURCE_EDUCATION_ASSESSMENT,
    RESOURCE_GRADING,
    RESOURCE_REFERRAL,
    RESOURCE_PSS_SERVICE,
    RESOURCE_INCLUSION_SERVICE,
    RESOURCE_DIGITAL_SERVICE,
    RESOURCE_HEALTH_NUTRITION_SERVICE,
    RESOURCE_HEALTH_NUTRITION_REFERRAL,
    RESOURCE_YOUTH_KIT_SERVICE,
    RESOURCE_YOUTH_SERVICE,
    RESOURCE_YOUTH_ASSESSMENT,
    RESOURCE_YOUTH_REFERRAL,
    RESOURCE_FOLLOW_UP_SERVICE,
    RESOURCE_RECREATIONAL,
    RESOURCE_LEGO_SERVICE,
    RESOURCE_ATTENDANCE,
]

#: Human readable labels, used by the Django admin on both sides.
RESOURCE_LABELS = (
    (RESOURCE_ROUND, 'Round'),
    (RESOURCE_PACKAGE, 'Package'),
    (RESOURCE_CENTER, 'Center'),
    (RESOURCE_TEACHER, 'Teacher'),
    (RESOURCE_REGISTRATION, 'Registration'),
    (RESOURCE_EDUCATION_SERVICE, 'Child education situation'),
    (RESOURCE_EDUCATION_RS_SERVICE, 'Education RS service'),
    (RESOURCE_EDUCATION_ASSESSMENT, 'Education assessment'),
    (RESOURCE_GRADING, 'Grading'),
    (RESOURCE_REFERRAL, 'Referral'),
    (RESOURCE_PSS_SERVICE, 'PSS service'),
    (RESOURCE_INCLUSION_SERVICE, 'Inclusion service'),
    (RESOURCE_DIGITAL_SERVICE, 'Digital service'),
    (RESOURCE_HEALTH_NUTRITION_SERVICE, 'Health & nutrition service'),
    (RESOURCE_HEALTH_NUTRITION_REFERRAL, 'Health & nutrition referral'),
    (RESOURCE_YOUTH_KIT_SERVICE, 'Youth kit service'),
    (RESOURCE_YOUTH_SERVICE, 'Youth service'),
    (RESOURCE_YOUTH_ASSESSMENT, 'Youth assessment'),
    (RESOURCE_YOUTH_REFERRAL, 'Youth referral'),
    (RESOURCE_FOLLOW_UP_SERVICE, 'Follow-up service'),
    (RESOURCE_RECREATIONAL, 'Recreational'),
    (RESOURCE_LEGO_SERVICE, 'LEGO service'),
    (RESOURCE_ATTENDANCE, 'Attendance'),
    (RESOURCE_CHILD, 'Child'),
)

#: Which replicated service each ``ProvidedServices`` checklist row points at
#: through its ``service_id``. Mirrors the ``update_service(...)`` calls in the
#: Compiler's MSCC forms. "Health and Nutrition" is shared by two models; the
#: producer resolves which one by checking which of them owns the id.
SERVICE_NAME_RESOURCES = {
    'PSS': (RESOURCE_PSS_SERVICE,),
    'Inclusion': (RESOURCE_INCLUSION_SERVICE,),
    'Digital component': (RESOURCE_DIGITAL_SERVICE,),
    'Health and Nutrition': (
        RESOURCE_HEALTH_NUTRITION_SERVICE,
        RESOURCE_HEALTH_NUTRITION_REFERRAL,
    ),
    'Adolescents kit': (RESOURCE_YOUTH_KIT_SERVICE,),
    'Caregivers Package': (RESOURCE_FOLLOW_UP_SERVICE,),
    'LEGO': (RESOURCE_LEGO_SERVICE,),
    'RS': (RESOURCE_EDUCATION_RS_SERVICE,),
}

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
