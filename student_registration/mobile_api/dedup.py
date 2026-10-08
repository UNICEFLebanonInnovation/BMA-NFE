# -*- coding: utf-8 -*-
"""Server-side duplicate verification for offline-collected registrations.

Mirrors ``mscc.views.child_duplication_check`` (UNICEF unique id) and adds a
deterministic local identity check so the verification works even when the
external Unique-ID service is unreachable.
"""
from __future__ import unicode_literals

import logging
import re
import unicodedata
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeout

from django.conf import settings
from django.db.models import Q

logger = logging.getLogger(__name__)

ARABIC_FOLD = {
    'أ': 'ا', 'إ': 'ا', 'آ': 'ا', 'ٱ': 'ا',  # alef variants
    'ة': 'ه',  # taa marbuta → haa
    'ى': 'ي',  # alef maqsura → yaa
    'ـ': '',        # tatweel
}
_DIACRITICS = re.compile(r'[ً-ٰٟ]')
_SPACES = re.compile(r'\s+')

ID_NUMBER_FIELDS = (
    'id_number', 'individual_case_number', 'case_number', 'recorded_number', 'national_number',
    'syrian_national_number', 'sop_national_number', 'other_number', 'individual_extract_record',
    'parent_individual_case_number', 'parent_national_number', 'parent_syrian_national_number',
    'parent_sop_national_number', 'parent_other_number', 'parent_extract_record',
)
CHILD_ID_FIELDS = (
    'individual_case_number', 'case_number', 'recorded_number', 'national_number',
    'syrian_national_number', 'sop_national_number', 'other_number',
)
STUDENT_ID_FIELDS = ('id_number',)
BRIDGING_ID_FIELDS = (
    'individual_case_number', 'recorded_number', 'national_number', 'syrian_national_number',
    'sop_national_number', 'other_number', 'individual_extract_record',
)


def normalize_name(value):
    if not value:
        return ''
    text = unicodedata.normalize('NFKC', str(value))
    text = _DIACRITICS.sub('', text)
    text = ''.join(ARABIC_FOLD.get(ch, ch) for ch in text)
    text = _SPACES.sub(' ', text).strip().lower()
    return text


def _clean_number(value):
    if value is None:
        return ''
    value = str(value).strip()
    if value in ('', '0', 'None', 'null'):
        return ''
    return value


class Identity(object):
    """Identity fields extracted from a push payload."""

    def __init__(self, first_name, father_name, last_name, mother_fullname, gender,
                 birthday_year, birthday_month, birthday_day, nationality_id, id_numbers):
        self.first_name = first_name or ''
        self.father_name = father_name or ''
        self.last_name = last_name or ''
        self.mother_fullname = mother_fullname or ''
        self.gender = (gender or '').strip()
        self.birthday_year = str(birthday_year or '').strip()
        self.birthday_month = str(birthday_month or '').strip()
        self.birthday_day = str(birthday_day or '').strip()
        self.nationality_id = nationality_id
        self.id_numbers = [n for n in id_numbers if n]

    @property
    def complete(self):
        return all([self.first_name, self.father_name, self.last_name, self.gender,
                    self.birthday_year, self.birthday_month, self.birthday_day])

    @property
    def names_key(self):
        return (normalize_name(self.first_name), normalize_name(self.father_name),
                normalize_name(self.last_name), normalize_name(self.mother_fullname))

    @property
    def birthdate(self):
        return '{}-{}-{}'.format(self.birthday_year, self.birthday_month, self.birthday_day)

    def nationality_name_en(self):
        from student_registration.students.models import Nationality
        if not self.nationality_id:
            return ''
        try:
            return Nationality.objects.get(pk=self.nationality_id).name_en or ''
        except (Nationality.DoesNotExist, ValueError, TypeError):
            return ''


def identity_from_payload(spec, data):
    """Read identity fields with the entity's person prefix (``child_``/``student_``)."""
    p = spec.person_prefix
    gender_key = p + ('sex' if spec.person_field == 'student' else 'gender')
    if spec.person_field == 'student':
        id_fields = BRIDGING_ID_FIELDS
    else:
        id_fields = CHILD_ID_FIELDS
    return Identity(
        first_name=data.get(p + 'first_name'),
        father_name=data.get(p + 'father_name'),
        last_name=data.get(p + 'last_name'),
        mother_fullname=data.get(p + 'mother_fullname'),
        gender=data.get(gender_key),
        birthday_year=data.get(p + 'birthday_year'),
        birthday_month=data.get(p + 'birthday_month'),
        birthday_day=data.get(p + 'birthday_day'),
        nationality_id=data.get(p + 'nationality'),
        id_numbers=[_clean_number(data.get(f)) for f in id_fields],
    )


def call_with_timeout(fn, timeout, *args, **kwargs):
    executor = ThreadPoolExecutor(max_workers=1)
    future = executor.submit(fn, *args, **kwargs)
    try:
        return future.result(timeout=timeout)
    except FuturesTimeout:
        logger.warning('External call %s timed out after %ss', getattr(fn, '__name__', fn), timeout)
        return None
    except Exception as ex:  # pragma: no cover - external failures are non fatal
        logger.warning('External call %s failed: %s', getattr(fn, '__name__', fn), ex)
        return None
    finally:
        executor.shutdown(wait=False)


def external_unique_id(identity):
    """UNICEF unique id from the external service, or ``None`` when unavailable."""
    if not getattr(settings, 'MOBILE_API_USE_UNIQUE_ID_SERVICE', True):
        return None
    from student_registration.students.utils import generate_one_unique_id
    timeout = getattr(settings, 'MOBILE_API_UNIQUE_ID_TIMEOUT', 8)
    result = call_with_timeout(
        generate_one_unique_id, timeout, '0', identity.first_name, identity.father_name,
        identity.last_name, identity.mother_fullname, identity.birthdate,
        identity.nationality_name_en(), identity.gender,
    )
    if result in (None, 0, '0', ''):
        return None
    return str(result)


def _person_models(spec):
    from student_registration.alp.models import ALPRegistration
    from student_registration.child.models import Child
    from student_registration.clm.models import Bridging
    from student_registration.mscc.models import Registration
    from student_registration.students.models import Student
    if spec.key == 'mscc.registration':
        return Child, Registration, 'gender', 'child'
    if spec.key == 'alp.registration':
        return Child, ALPRegistration, 'gender', 'child'
    if spec.key == 'clm.bridging':
        return Student, Bridging, 'sex', 'student'
    raise ValueError('Entity {} has no identity'.format(spec.key))


def _year_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def find_duplicates(spec, identity, exclude_person_id=None, use_external=True):
    """Return candidate duplicates as a list of dicts (empty when none)."""
    Person, RegModel, gender_field, person_fk = _person_models(spec)
    matches = {}  # person_id -> (reason, score, fields)

    def _add(person_id, reason, score, fields):
        if exclude_person_id and person_id == exclude_person_id:
            return
        current = matches.get(person_id)
        if current is None or score > current[1]:
            matches[person_id] = (reason, score, fields)

    # 1. UNICEF unique id (same rule as the website).
    if use_external and identity.complete:
        unicef_id = external_unique_id(identity)
        if unicef_id:
            for pid in Person.objects.filter(unicef_id=unicef_id).values_list('id', flat=True):
                _add(pid, 'unicef_id', 1.0, ['unicef_id'])

    # 2 + 4. Local identity key (exact) and near matches (birth year ± 1).
    year = _year_int(identity.birthday_year)
    if identity.complete and year:
        names_key = identity.names_key
        candidates = Person.objects.filter(
            **{gender_field: identity.gender},
            birthday_year__in=[str(year - 1), str(year), str(year + 1)],
        ).only('id', 'first_name', 'father_name', 'last_name', 'mother_fullname',
               'birthday_year', 'birthday_month', 'birthday_day')
        for person in candidates.iterator():
            key = (normalize_name(person.first_name), normalize_name(person.father_name),
                   normalize_name(person.last_name), normalize_name(person.mother_fullname))
            if key[:3] != names_key[:3]:
                continue
            same_mother = key[3] == names_key[3] or not names_key[3] or not key[3]
            same_dob = (str(person.birthday_year) == identity.birthday_year and
                        str(person.birthday_month) == identity.birthday_month and
                        str(person.birthday_day) == identity.birthday_day)
            if same_dob and same_mother:
                _add(person.id, 'identity', 1.0, ['names', 'mother', 'birthday', 'gender'])
            elif same_dob:
                _add(person.id, 'near', 0.8, ['names', 'birthday', 'gender'])
            elif same_mother:
                _add(person.id, 'near', 0.6, ['names', 'mother', 'gender'])

    # 3. Identical identity-document numbers.
    if identity.id_numbers:
        if person_fk == 'child':
            q = Q()
            for number in identity.id_numbers:
                for f in CHILD_ID_FIELDS:
                    q |= Q(**{f: number})
            for pid in Person.objects.filter(q).values_list('id', flat=True):
                _add(pid, 'id_number', 1.0, ['id_number'])
        else:
            q = Q()
            for number in identity.id_numbers:
                for f in BRIDGING_ID_FIELDS:
                    q |= Q(**{f: number})
                q |= Q(student__id_number=number)
            for pid in RegModel.objects.filter(q).values_list('student_id', flat=True):
                if pid:
                    _add(pid, 'id_number', 1.0, ['id_number'])

    if not matches:
        return []

    return _build_candidates(spec, RegModel, Person, person_fk, matches)


def _build_candidates(spec, RegModel, Person, person_fk, matches):
    person_ids = list(matches.keys())
    registrations = (RegModel.objects.filter(**{person_fk + '_id__in': person_ids}, deleted=False)
                     .select_related(person_fk).order_by('-id'))
    seen = set()
    results = []
    for reg in registrations:
        person = getattr(reg, person_fk)
        if person is None:
            continue
        seen.add(person.id)
        results.append(_candidate(spec, reg, person, matches[person.id]))
    # Persons without a live registration are still reported (can be linked).
    for person in Person.objects.filter(id__in=[p for p in person_ids if p not in seen]):
        results.append(_candidate(spec, None, person, matches[person.id]))
    results.sort(key=lambda c: (-c['match']['score'], -(c['registration_id'] or 0)))
    return results[:20]


def _candidate(spec, reg, person, match):
    reason, score, fields = match
    gender = getattr(person, 'gender', None) or getattr(person, 'sex', None)
    nationality = getattr(person, 'nationality', None)
    data = {
        'registration_id': reg.id if reg is not None else None,
        'child_id': person.id,
        'label': '{} {} {}'.format(person.first_name or '', person.father_name or '',
                                   person.last_name or '').strip(),
        'mother_fullname': person.mother_fullname,
        'birthday': '{}-{}-{}'.format(person.birthday_year, person.birthday_month, person.birthday_day),
        'gender': gender,
        'nationality': str(nationality) if nationality else None,
        'number': getattr(person, 'number', None),
        'unicef_id': getattr(person, 'unicef_id', None),
        'center': None, 'school': None, 'partner': None, 'round': None,
        'match': {'reason': reason, 'score': score, 'fields': fields},
    }
    if reg is not None:
        for attr in ('center', 'school', 'partner', 'round'):
            value = getattr(reg, attr, None) if hasattr(reg, attr) else None
            data[attr] = str(value) if value else None
        data['registration_date'] = reg.registration_date.isoformat() \
            if getattr(reg, 'registration_date', None) else None
        data['created'] = reg.created.isoformat() if getattr(reg, 'created', None) else None
    return data
