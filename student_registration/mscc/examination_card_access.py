"""Programme eligibility shared by individual and bulk examination cards.

RS children do not receive an examination card. The current programme is the
latest EducationService, matching Registration.education_program; historical
RS service details must not hide a card after a programme change.
"""

from django.db.models import OuterRef, Q, Subquery

from .models import EducationService


RS_PROGRAMMES = frozenset(
    ["RS Grade {}".format(grade) for grade in range(1, 10)]
    + ["YFS Level 1 - RS Grade 9", "YFS Level 2 - RS Grade 9"]
)
_PROGRAMME_ANNOTATION = "_examination_card_programme"


def registration_can_have_examination_card(registration):
    """Return whether the registration's current programme permits a card.

    Reuse the SQL annotation supplied by the bulk filter or prefetched services
    when available, so checking each row does not add another database query.
    Access to the registration itself remains the caller's responsibility.
    """
    if hasattr(registration, _PROGRAMME_ANNOTATION):
        programme = getattr(registration, _PROGRAMME_ANNOTATION)
    elif "education_service" in getattr(
        registration, "_prefetched_objects_cache", {}
    ):
        services = registration._prefetched_objects_cache["education_service"]
        latest = max(services, key=lambda service: service.pk, default=None)
        programme = latest.education_program if latest is not None else None
    elif registration.pk is None:
        programme = None
    else:
        programme = (
            registration.education_service.order_by("-pk")
            .values_list("education_program", flat=True)
            .first()
        )
    return programme not in RS_PROGRAMMES


def filter_examination_card_registrations(queryset):
    """Filter a caller-scoped queryset to registrations eligible for a card.

    A correlated subquery selects only the current programme, rather than
    excluding registrations that happened to receive RS in an older service.
    Registrations without an education service retain their existing access.
    """
    latest_programme = (
        EducationService.objects.filter(registration_id=OuterRef("pk"))
        .order_by("-pk")
        .values("education_program")[:1]
    )
    queryset = queryset.annotate(
        **{_PROGRAMME_ANNOTATION: Subquery(latest_programme)}
    )
    return queryset.filter(
        Q(**{_PROGRAMME_ANNOTATION + "__isnull": True})
        | ~Q(**{_PROGRAMME_ANNOTATION + "__in": RS_PROGRAMMES})
    )
