from django import template

register = template.Library()


@register.simple_tag
def get_education_programme_assessments(result1, result, request=None):
    if not result1 or not result1.education_program:
        return []

    prog = result1.education_program

    assessments = []

    # helper for adding assessments
    def add(key, label, max_score=None, pre_max_score=None, post_max_score=None, pre_val=None, post_val=None, school_val=None, imp_val=None, pre_label=None, post_label=None):
        pre_max = pre_max_score if pre_max_score is not None else max_score
        post_max = post_max_score if post_max_score is not None else max_score
        assessments.append({
            'key': key,
            'label': label,
            'pre_label': pre_label or label,
            'post_label': post_label or label,
            'max_score': max_score,
            'pre_max_score': pre_max,
            'post_max_score': post_max,
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

    if prog in ['BLN Level 1', 'BLN Level 2', 'BLN Level 3']:
        add('arabic_grade', 'Arabic Language Development', 20)
        if provide_french:
            add('french_grade', 'French Language Development', 30)
        else:
            add('english_grade', 'English Language Development', 30)
        add('math_grade', 'Mathematics', 25, pre_max_score=25, post_max_score=20)
    elif prog == 'CBECE Level 1':
        add('language_grade', 'Language Development', 48)
        add('math_grade', 'Cognitive Development - Mathematics', 24)
        add('science_grade', 'Cognitive Development - Science', 18)
        add('social_emotional_grade', 'Social-Emotional Development', 14)
        add('psychomotor_grade', 'Psychomotor Development', 20)
        add('artistic_grade', 'Artistic Development', 10)
    elif prog == 'CBECE Level 2':
        add('arabic_grade', 'Arabic Language Development', 66)
        add('language_grade', 'Language Development', 66, pre_label='Language Development', post_label='Foreign Language Development')
        add('math_grade', 'Cognitive Development - Mathematics', 48)
        add('science_grade', 'Cognitive Development - Science', 38)
        add('social_emotional_grade', 'Social-Emotional Development', 40)
        add('psychomotor_grade', 'Psychomotor Development', 40)
        add('artistic_grade', 'Artistic Development', 16)
    elif prog == 'CBECE Level 3':
        add('arabic_grade', 'Arabic Language Development', 74)
        add('language_grade', 'Language Development', 74, pre_label='Language Development', post_label='Foreign Language Development')
        add('math_grade', 'Cognitive Development - Mathematics', 50)
        add('science_grade', 'Cognitive Development - Science', 38)
        add('social_emotional_grade', 'Social-Emotional Development', 40)
        add('psychomotor_grade', 'Psychomotor Development', 42)
        add('artistic_grade', 'Artistic Development', 16)
    elif prog in ['RS Grade 1', 'RS Grade 2', 'RS Grade 3']:
        add('arabic_grade', 'Arabic Development', 20)
        add('language_grade', 'Foreign Language', 20)
        add('math_grade', 'Mathematics', 20)
        add('science_grade', 'Science', 20)
    elif prog == 'YBLN Level 1':
        add('arabic_grade', 'Arabic Language Development', 12)
        add('language_grade', 'Foreign Language Development', 0)
        add('math_grade', 'Mathematics', 15)
        add('life_skills', 'Life Skills Development', 12)
    elif prog == 'YBLN Level 2':
        add('arabic_grade', 'Arabic Language Development', 12)
        add('language_grade', 'Foreign Language Development', 12)
        add('math_grade', 'Mathematics', 21)
        add('life_skills', 'Life Skills Development', 12)

    return assessments
