from student_registration.users.templatetags.custom_tags import has_group

def user_has_alp_permission(user):
    return has_group(user, 'ALP_SCHOOL')

def filter_by_school(queryset, user):
    """
    Filter the queryset to only include records related to the user's school.
    Superusers can see all records.
    """
    if user.is_superuser:
        return queryset

    # We assume models have a `school` field directly, except Attendance which has `registration__school` or `teacher__school`.
    # Let's handle different models.
    model_name = queryset.model.__name__

    if model_name in ['ALPRegistration', 'ALPTeacher']:
        return queryset.filter(school=user.school)
    elif model_name == 'ALPAttendance':
        return queryset.filter(registration__school=user.school)
    elif model_name == 'ALPTeacherAttendance':
        return queryset.filter(teacher__school=user.school)
    elif model_name == 'ALPGrading':
        return queryset.filter(registration__school=user.school)

    return queryset
