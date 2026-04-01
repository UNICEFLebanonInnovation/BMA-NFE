from django import template
from student_registration.mscc.models import EducationProgrammeGrading

register = template.Library()


@register.simple_tag
def get_education_programme_assessments(result1, result, request=None):
    if not result1 or not result1.education_program:
        return []

    prog = result1.education_program

    assessments = []

    # helper for adding assessments
    def add(key, label, max_score=None, pre_val=None, post_val=None, school_val=None, imp_val=None, pre_label=None, post_label=None):
        assessments.append({
            'key': key,
            'label': label,
            'pre_label': pre_label or label,
            'post_label': post_label or label,
            'max_score': max_score,
            'pre': pre_val if pre_val is not None else (result.pre_test.get(key) if result and hasattr(result, 'pre_test') and result.pre_test else None),
            'post': post_val if post_val is not None else (result.post_test.get(key) if result and hasattr(result, 'post_test') and result.post_test else None),
            'school': school_val if school_val is not None else (result.school_test.get(key) if result and hasattr(result, 'school_test') and result.school_test else None),
            'imp': imp_val if imp_val is not None else grading_improvement_calc(result, key),
        })

    def grading_improvement_calc(instance, field):
        if not instance:
            return 0
        if not hasattr(instance, 'pre_test') or not hasattr(instance, 'post_test'):
            return 0
        if not instance.pre_test or not instance.post_test:
            return 0
        pre_value = instance.pre_test.get(field, 0)
        post_value = instance.post_test.get(field, 0)
        if pre_value and post_value:
            try:
                return '{}{}'.format(
                    round(((float(post_value) - float(pre_value)) /
                           float(pre_value)) * 100.0, 2), '%')
            except ZeroDivisionError:
                return 0.0
            except ValueError:
                return 0.0
        return 0.0

    provide_french = False
    if request and request.user and hasattr(request.user, 'center') and request.user.center:
        provide_french = getattr(request.user.center, 'provide_french_language', 'No') == 'Yes'

    gradings = EducationProgrammeGrading.objects.filter(programme_type=prog).order_by('order')

    for grading in gradings:
        if grading.condition == 'french_only' and not provide_french:
            continue
        if grading.condition == 'english_only' and provide_french:
            continue

        pre_label = grading.label
        post_label = grading.label

        # Keep CBECE Level 2 & 3 legacy behavior where language_grade pre_label is Language Development and post_label is Foreign Language Development
        if prog in ['CBECE Level 2', 'CBECE Level 3'] and grading.key == 'language_grade':
            pre_label = 'Language Development'
            post_label = 'Foreign Language Development'

        add(grading.key, grading.label, grading.max_score, pre_label=pre_label, post_label=post_label)

    return assessments
