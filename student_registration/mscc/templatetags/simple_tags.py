from django import template
from django.apps import apps
from django.db.models import QuerySet
import logging
from typing import Iterable, Union
from collections import defaultdict


from student_registration.mscc.models import (
    ProvidedServices,
    EducationHistory,
    Registration,
    EducationService,
    Round,
    Packages,
)
from student_registration.attendances.models import MSCCAttendance, MSCCAttendanceChild


register = template.Library()
logger = logging.getLogger(__name__)

_SERVICES_CACHE_ATTR = "_provided_services_cache"


def _get_services_for_registry(registry: Union[int, "Registration", str, None]) -> list:

    if not registry:
        return []

    try:
        if isinstance(registry, Registration):
            registry_obj = registry
        elif isinstance(registry, int):
            registry_obj = Registration.objects.get(pk=registry)
        elif isinstance(registry, str):
            registry_obj = Registration.objects.get(pk=int(registry))
        else:
            return []
    except (ValueError, Registration.DoesNotExist):
        return []

    cached_services = getattr(registry_obj, _SERVICES_CACHE_ATTR, None)
    if cached_services is not None:
        return cached_services

    services = list(
        ProvidedServices.objects
        .filter(registration=registry_obj)
        .order_by("id")
    )
    setattr(registry_obj, _SERVICES_CACHE_ATTR, services)
    return services


def _coerce_services(services, registry=None):
    if isinstance(services, dict):
        return list(services.values())

    if isinstance(services, list):
        return services

    if isinstance(services, QuerySet):
        if registry is not None:
            return _get_services_for_registry(registry)
        return list(services.order_by("id"))

    if services is None and registry is not None:
        return _get_services_for_registry(registry)

    try:
        return list(services)
    except TypeError:
        if registry is not None:
            return _get_services_for_registry(registry)
        return []


def _get_service_by_name(services, service_name):
    for service in reversed(services):
        if service.name == service_name:
            return service
    return None


@register.simple_tag
def have_service(services, service_name):
    if isinstance(services, dict):
        return services.get(service_name)

    for service in _coerce_services(services):
        if service.name == service_name:
            return service

    return None


@register.simple_tag
def get_service_info(services, registry, service_name):
    service_list = _coerce_services(services, registry)
    return _get_service_by_name(service_list, service_name)


@register.simple_tag
def get_child_fullname(registry):
    reg = Registration.objects.filter(id=registry).last()
    if reg:
        return reg.child_fullname
    return None


@register.simple_tag
def get_regitration_type(registry):
    reg = Registration.objects.filter(id=registry).last()
    return reg.type


@register.simple_tag
def get_child_rounds(registry):
    from django.db.models import Subquery
    registration_ids = Registration.objects.filter(
        child_id=Subquery(
            Registration.objects.filter(id=registry).values('child_id')[:1]
        )
    ).values_list('id', flat=True)
    round_names = Round.objects.filter(
        id__in=EducationService.objects.filter
        (registration_id__in=registration_ids,
         registration__deleted=False).values_list('round_id',flat=True)).values_list('name', flat=True).distinct()

    if round_names:
        return round_names
    else:
        return None


@register.simple_tag
def get_service(registry, service_name):
    services = _get_services_for_registry(registry)
    return _get_service_by_name(services, service_name)


@register.simple_tag
def get_youth_services(registry,service_name):
    if type(registry) == 'int':
        return Packages.objects.filter(
            type=registry.type,
            min_age__lte=registry.child_age,
            max_age__gte=registry.child_age
        ).last()
    return Packages.objects.filter(
        type=registry.type,
        min_age__lte=registry.child_age,
        max_age__gte=registry.child_age
    ).last()


@register.simple_tag
def get_education_service(registry):
    if type(registry) == 'int':
        education_service = EducationService.objects.filter(registration_id=registry).last()
    education_service = EducationService.objects.filter( registration=registry).last()
    if education_service:
        return education_service.education_program
    else:
        return None


@register.simple_tag
def get_service_all(registry, model_name):
    try:
        model = apps.get_model('mscc', model_name)
        return model.objects.filter(registration=registry)
    except Exception as ex:
        return False


@register.simple_tag
def get_education_service_history(child_id):
    try:
        return EducationService.objects.filter( registration__child_id=child_id,registration__deleted=False)\
            .order_by('registration_date')

    except Exception as ex:
        return False


@register.simple_tag
def get_services(registry):
    return _get_services_for_registry(registry)


@register.simple_tag
def get_completion_rate(registry):
    services = _get_services_for_registry(registry)
    nbr_services = len(services)
    nbr_completed = len([service for service in services if service.completed])
    try:
        return int(round(float(nbr_completed)/float(nbr_services), 2) * 100.0)
    except Exception as ex:
        return 0


@register.simple_tag
def service_completed(services, service_name):
    for service in _coerce_services(services):
        if service.name == service_name and service.completed:
            return True
    return False


@register.simple_tag
def service_required(services, service_name):
    for service in _coerce_services(services):
        if service.name == service_name and service.required:
            return True
    return False


@register.simple_tag
def service_info(services, service_name):
    return [
        service
        for service in _coerce_services(services)
        if service.name == service_name
    ]


@register.simple_tag
def have_service_category(category, obj):
    try:
        services = _get_services_for_registry(obj)
        return len([service for service in services if service.category == category])
    except Exception as ex:
        return False


@register.simple_tag
def have_education_programme(programme_type):
    try:
        return (
            Packages.objects
                .filter(category='Education', name=programme_type)
                .values_list('name', flat=True)
                .first()
        )
    except Exception as ex:
        return False


@register.simple_tag
def have_youth_programme(programme_type):
    try:
        programmes = ['YBLN Level 1', 'YBLN Level 2','YBLN Catch-up',
                      'YFS Level 1', 'YFS Level 2',
                      'YFS Level 1 - RS Grade 9', 'YFS Level 2 - RS Grade 9']
        if programme_type in programmes:
            return True
    except Exception as ex:
        return False


@register.simple_tag
def service_data(model_name, obj):
    try:
        model = apps.get_model('mscc', model_name)
        return model.objects.filter(registration=obj).last()
    except Exception as ex:
        return False

@register.simple_tag
def service_youth_data(model_name, obj, service_type):
    try:
        model = apps.get_model('mscc', model_name)
        return model.objects.filter(registration=obj, service_type=service_type).last()
    except Exception as ex:
        return False

@register.simple_tag
def education_history(registration_id):
    return EducationHistory.objects.filter(registration_id=registration_id)


@register.simple_tag
def education_history_programmes(student_id):
    try:
        programmes = []
        programme_types = ['BLN', 'ABLN', 'Bridging', 'RS', 'CBECE', 'Inclusion']

        for programme_type in programme_types:
            if education_history_programme(programme_type, student_id):
                programmes.append(programme_type)

        return ", ".join(programmes)
    except Exception as ex:
        return ''


def education_history_programme(model_name, student_id):
    try:
        model = apps.get_model('clm', model_name)
        e = model.objects.filter(student_id=student_id).exists()
        return e
    except Exception as ex:
        return False


@register.simple_tag
def education_history_model(programme_id, programme_type):
    try:
        model = apps.get_model('clm', programme_type)
        model_data = model.objects.get(id=programme_id)
        return model_data
    except Exception as ex:
        return None


@register.simple_tag
def get_educations_data(obj):
    try:
        history = education_history(obj)

        # Group programme IDs by programme type to minimize queries
        programmes_by_type = defaultdict(list)
        for item in history:
            programmes_by_type[item.programme_type].append(item.programme_id)

        # Fetch all related models in bulk
        fetched_models = {}
        for p_type, p_ids in programmes_by_type.items():
            model = apps.get_model('clm', p_type)
            # Fetch all matching objects and store them in a dict keyed by (programme_type, id)
            for model_data in model.objects.filter(id__in=p_ids):
                fetched_models[(p_type, model_data.id)] = model_data

        educations = []
        for item in history:
            model_data = fetched_models.get((item.programme_type, item.programme_id))
            if model_data:
                educations.append({
                    'programme_type': item.programme_type,
                    'programme_id': item.programme_id,
                    'round': model_data.round,
                    'registration_level': model_data.registration_level,
                    'center': model_data.center,
                    'registration_date': model_data.registration_date
                })
        return educations
    except Exception as ex:
        logger.exception(ex)
        return []


@register.simple_tag
def child_attendance(child_id):
    try:
        return MSCCAttendanceChild.objects.filter(child_id=child_id)

    except Exception as ex:
        logger.exception(ex)
        return []


@register.simple_tag
def child_attendance_history(child_id):
    try:
        details = {}
        from datetime import datetime
        today = datetime.today()

        attendances = MSCCAttendanceChild.objects.filter(child_id=child_id)

        details['ttl_days'] = attendances.count()
        details['ttl_attended'] = attendances.filter(attended='Yes').count()
        details['ttl_absence'] = attendances.filter(attended='No').count()
        details['ttl_absence_month'] = attendances.filter(attended='No',
                                                          attendance_day__attendance_date__month=today.month).count()
        details['ttl_off'] = 0

        return details
    except Exception as ex:
        logger.exception(ex)
        return []


@register.simple_tag
def eligible_to_followup(registry):
    try:
        disability = True if registry.child.disability else False
        if disability:
            return True

        referral = service_data('Referral', registry)
        if referral and referral.referred_service == 'CP':
            return True

        if ProvidedServices.objects.filter(name='PSS', registration=registry).exists():
            return True

        return False
    except Exception as ex:
        return False


@register.simple_tag
def grading_improvement(instance, field):
    if not instance:
        return 0
    if not instance.pre_test or not instance.post_test:
        return 0
    pre_value = instance.pre_test[field] if field in instance.pre_test else 0
    post_value = instance.post_test[field] if field in instance.post_test else 0
    if pre_value and post_value:
        try:
            return '{}{}'.format(
                round(((float(post_value) - float(pre_value)) /
                       float(pre_value)) * 100.0, 2), '%')
        except ZeroDivisionError:
            return 0.0
    return 0.0


@register.filter
def month_name(value):
    """Return the localised month name for a 1-12 month number.

    ``django.utils.dates.MONTHS`` values are lazily translated, so Arabic
    users see Arabic month names instead of the hard-coded English list that
    used to live in the attendance templates.
    """
    from django.utils.dates import MONTHS
    try:
        return MONTHS[int(value)]
    except (TypeError, ValueError, KeyError):
        return ''
