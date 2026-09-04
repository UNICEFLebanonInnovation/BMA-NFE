import json
from django import template
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import Group
import datetime

register = template.Library()


@register.simple_tag
def get_range(start, end):
    return (str(x) for x in range(start, end))


@register.simple_tag
def get_range_int(start, end):
    return (x for x in range(start, end))


@register.simple_tag
def get_range_str(start, end):
    return (str(x-1)+'/'+str(x) for x in range(start, end))


@register.simple_tag
def get_range_years(start=1990, end=2051):
    return (str(x) for x in range(start, end))


@register.simple_tag
def get_range_months(start=1, end=13):
    return (str(x) for x in range(start, end))


@register.simple_tag
def get_range_days(start=1, end=31):
    return (str(x) for x in range(start, end))


@register.filter
def json_loads(data):
    return json.loads(data)


@register.simple_tag
def json_load_value(data, key):
    key = key.replace("column", "field")
    list = json.loads(data)
    if key in list:
        return list[key]
    return ''


@register.simple_tag
def get_user_token(user_id):
    # token = Token.objects.get_or_create(user_id=user_id)
    try:
        token = Token.objects.get(user_id=user_id)
    except Token.DoesNotExist:
        token = Token.objects.create(user_id=user_id)
    return token.key


@register.filter(name='has_group')
def has_group(user, group_name):
    if not user:
        return False
    # Super users should have access to all groups
    if getattr(user, "is_superuser", False):
        return True
    try:
        group = Group.objects.get(name=group_name)
        return group in user.groups.all()
    except Group.DoesNotExist:
        return False


@register.filter(name='is_owner')
def is_owner(user, instance):
    try:
        if user == instance.owner:
            return True
    except Group.DoesNotExist:
        pass
    return False


@register.filter(name='user_main_role')
def user_main_role(user):
    groups = user.groups.all()
    if 'PMU' in groups:
        return 'pmu'
    if 'COORDINATOR' in groups:
        return 'coordinator'
    if 'DIRECTOR' in groups:
        return 'director'
    if 'SCHOOL' in groups:
        return 'school'
    return 'mehe'


@register.filter(name='is_current_page')
def is_current_page(request, url_name):
    # path_info = request.META.get('PATH_INFO', '')
    # current_url = resolve(path_info).url_name
    # if url_name == current_url:
    #     return True
    return False


@register.filter(name='multiply')
def multiply(value, arg):
    return value*arg


@register.filter(name='percentage')
def percentage(number, total):
    if number:
        return round((number*100.0)/total, 2)
    return 0


@register.filter(name='percentage_int')
def percentage_int(number, total):
    if number:
        return int(round((number*100.0)/total, 2))
    return 0


@register.simple_tag
def enrollment_by_gov_by_grade_by_gender(registrations, gov, level=None, gender=None):
    if gender:
        registrations = registrations.filter(student__sex=gender)
    if gov:
        registrations = registrations.filter(school__location__parent_id=gov)
    if level:
        registrations = registrations.filter(classroom_id=level)
    return registrations.count()


@register.simple_tag
def enrollment_by_school_by_grade_by_gender(registrations, school, level=None, gender=None):
    if gender:
        registrations = registrations.filter(student__sex=gender)
    if school:
        registrations = registrations.filter(school_id=school)
    if level:
        registrations = registrations.filter(classroom_id=level)
    return registrations.count()


@register.simple_tag
def enrollment_by_school_by_nationality_by_gender(registrations, school, nationality=None, gender=None):
    if gender:
        registrations = registrations.filter(student__sex=gender)
    if school:
        registrations = registrations.filter(school_id=school)
    if nationality:
        registrations = registrations.filter(student__nationality_id=nationality)
    return registrations.count()


@register.simple_tag
def enrollment_by_gov_by_nationality_by_gender(registrations, gov, nationality=None, gender=None):
    if gender:
        registrations = registrations.filter(student__sex=gender)
    if gov:
        registrations = registrations.filter(school__location__parent_id=gov)
    if nationality:
        registrations = registrations.filter(student__nationality_id=nationality)
    return registrations.count()


@register.simple_tag
def enrollment_by_gov_by_nationality_by_gender_by_grade(registrations, gov, nationality=None, gender=None, level=None):
    if gender:
        registrations = registrations.filter(student__sex=gender)
    if gov:
        registrations = registrations.filter(school__location__parent_id=gov)
    if nationality:
        registrations = registrations.filter(student__nationality_id=nationality)
    if level:
        registrations = registrations.filter(classroom_id=level)
    return registrations.count()


@register.simple_tag
def enrollment_by_gov_by_age_by_gender(registrations, gov, age=None, gender=None):
    now = datetime.datetime.now()
    if gender:
        registrations = registrations.filter(student__sex=gender)
    if gov:
        registrations = registrations.filter(school__location__parent_id=gov)
    if age:
        registrations = registrations.filter(student__birthday_year=(now.year - age))
    return registrations.count()


@register.simple_tag
def enrollment_by_grade_by_age_by_gender(registrations, grade, age=None, gender=None):
    now = datetime.datetime.now()
    if gender:
        registrations = registrations.filter(student__sex=gender)
    if grade:
        registrations = registrations.filter(classroom_id=grade)
    if age:
        registrations = registrations.filter(student__birthday_year=(now.year - age))
    return registrations.count()


@register.simple_tag
def enrollment_by_grade_by_nationality_by_gender(registrations, grade=None, nationality=None, gender=None):
    if gender:
        registrations = registrations.filter(student__sex=gender)
    if grade:
        registrations = registrations.filter(classroom_id=grade)
    if nationality:
        registrations = registrations.filter(student__nationality_id=nationality)
    return registrations.count()


@register.simple_tag
def enrollment_by_nationality_by_age_by_gender(registrations, nationality=None, age=None, gender=None):
    now = datetime.datetime.now()
    if gender:
        registrations = registrations.filter(student__sex=gender)
    if nationality:
        registrations = registrations.filter(student__nationality_id=nationality)
    if age:
        registrations = registrations.filter(student__birthday_year=(now.year - age))
    return registrations.count()


@register.simple_tag
def alp_by_gov_by_grade(registrations, gov, level):
    if not gov:
        return registrations.filter(registered_in_level=level).count()
    elif not level:
        return registrations.filter(registered_in_level__isnull=False, school__location__parent_id=gov).count()
    return registrations.filter(school__location__parent_id=gov, registered_in_level=level).count()


@register.simple_tag
def alp_by_gov_by_grade_by_gender(registrations, gov, level, gender):
    registrations = registrations.filter(student__sex=gender)
    if not gov:
        return registrations.filter(registered_in_level=level).count()
    elif not level:
        return registrations.filter(registered_in_level__isnull=False, school__location__parent_id=gov).count()
    return registrations.filter(school__location__parent_id=gov, registered_in_level=level).count()


@register.simple_tag
def alp_by_gov_by_assignedlevel_by_gender(registrations, gov, level, gender=None):
    if gender:
        registrations = registrations.filter(student__sex=gender)
    if not gov:
        return registrations.filter(assigned_to_level=level).count()
    elif not level:
        return registrations.filter(assigned_to_level__isnull=False, school__location__parent_id=gov).count()
    return registrations.filter(school__location__parent_id=gov, assigned_to_level=level).count()


@register.simple_tag
def alp_by_gov_by_referredlevel_by_gender(registrations, gov, level, gender=None):
    if gender:
        registrations = registrations.filter(student__sex=gender)
    if not gov:
        return registrations.filter(refer_to_level=level).count()
    elif not level:
        return registrations.filter(refer_to_level__isnull=False, school__location__parent_id=gov).count()
    return registrations.filter(school__location__parent_id=gov, refer_to_level=level).count()


@register.simple_tag
def alp_by_gov_by_age(registrations, gov, age=None):
    now = datetime.datetime.now()
    if not gov:
        return registrations.filter(student__birthday_year=(now.year - age)).count()
    elif age == 0:
        return registrations.filter(school__location__parent_id=gov, student__birthday_year=(now.year - age)).count()
    elif age == None:
        return registrations.filter(school__location__parent_id=gov).count()
    return registrations.filter(school__location__parent_id=gov, student__birthday_year=(now.year - age)).count()


@register.simple_tag
def alp_by_grade_by_age(registrations, level, age=None):
    now = datetime.datetime.now()
    if age == None:
        return registrations.filter(registered_in_level=level).count()
    elif not level:
        return registrations.filter(registered_in_level__isnull=False, student__birthday_year=(now.year - age)).count()
    return registrations.filter(registered_in_level=level, student__birthday_year=(now.year - age)).count()


@register.simple_tag
def alp_by_assignedlevel_by_age(registrations, level, age=None, and_above=False):
    now = datetime.datetime.now()
    if age == None:
        return registrations.filter(assigned_to_level=level).count()
    if not level:
        return registrations.filter(assigned_to_level__isnull=False, student__birthday_year=(now.year - age)).count()
    if and_above:
        return registrations.filter(assigned_to_level=level, student__birthday_year__lte=(now.year - age)).count()
    if age == 0:
        return registrations.filter(assigned_to_level=level, student__birthday_year__gte=(now.year - age)).count()
    return registrations.filter(assigned_to_level=level, student__birthday_year=(now.year - age)).count()


@register.simple_tag
def alp_by_referredlevel_by_age(registrations, level, age=None):
    now = datetime.datetime.now()
    if age == None:
        return registrations.filter(refer_to_level=level).count()
    elif not level:
        return registrations.filter(refer_to_level__isnull=False, student__birthday_year=(now.year - age)).count()
    return registrations.filter(refer_to_level=level, student__birthday_year=(now.year - age)).count()


@register.simple_tag
def get_item_by_key(dictionary, level, age):
    key = str(level)+'-'+str(age)
    return dictionary.get(key)


@register.filter
def get_item(dictionary, key):
    if not dictionary:
        return None
    return dictionary.get(key)


@register.filter
def get_label(field):
    if not field:
        return ''
    return getattr(field, 'label', '')


@register.filter
def is_allowed_create(programme):
    # The canonical implementation lives with the CLMRound model, in schools.utils.
    from student_registration.schools.utils import is_allowed_create
    return is_allowed_create(programme)


@register.filter
def is_allowed_edit(programme):
    from student_registration.schools.utils import is_allowed_edit
    return is_allowed_edit(programme)
