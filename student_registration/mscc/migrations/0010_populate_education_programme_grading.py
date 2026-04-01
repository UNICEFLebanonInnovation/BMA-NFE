from django.db import migrations

def populate_gradings(apps, schema_editor):
    EducationProgrammeGrading = apps.get_model('mscc', 'EducationProgrammeGrading')

    # helper for adding assessments
    def add(prog, key, label, max_score, condition='', order=0, form_type='education'):
        EducationProgrammeGrading.objects.create(
            programme_type=prog,
            key=key,
            label=label,
            max_score=max_score,
            condition=condition,
            order=order,
            form_type=form_type
        )

    # Data from education_tags.py and EducationGradingForm
    # BLN Level 1
    add('BLN Level 1', 'arabic_grade', 'Arabic Language Development', 68, order=1)
    add('BLN Level 1', 'french_grade', 'French Language Development', 43, condition='french_only', order=2)
    add('BLN Level 1', 'english_grade', 'English Language Development', 43, condition='english_only', order=3)
    add('BLN Level 1', 'math_grade', 'Mathematics', 22, order=4)

    # BLN Level 2
    add('BLN Level 2', 'arabic_grade', 'Arabic Language Development', 70, order=1)
    add('BLN Level 2', 'french_grade', 'French Language Development', 65, condition='french_only', order=2)
    add('BLN Level 2', 'english_grade', 'English Language Development', 65, condition='english_only', order=3)
    add('BLN Level 2', 'math_grade', 'Mathematics', 32, order=4)

    # BLN Level 3
    add('BLN Level 3', 'arabic_grade', 'Arabic Language Development', 69, order=1)
    add('BLN Level 3', 'french_grade', 'French Language Development', 59, condition='french_only', order=2)
    add('BLN Level 3', 'english_grade', 'English Language Development', 64, condition='english_only', order=3)
    add('BLN Level 3', 'math_grade', 'Mathematics', 32, order=4)

    # ABLN Level 1
    add('ABLN Level 1', 'arabic_grade', 'Arabic Language Development', 46, order=1)
    add('ABLN Level 1', 'math_grade', 'Mathematics', 20, order=2)
    add('ABLN Level 1', 'social_emotional_grade', 'Social-Emotional Development', 24, order=3)
    add('ABLN Level 1', 'artistic_grade', 'Artistic Development', 10, order=4)

    # ABLN Level 2
    add('ABLN Level 2', 'arabic_grade', 'Arabic Language Development', 56, order=1)
    add('ABLN Level 2', 'math_grade', 'Mathematics', 36, order=2)
    add('ABLN Level 2', 'social_emotional_grade', 'Social-Emotional Development', 24, order=3)
    add('ABLN Level 2', 'artistic_grade', 'Artistic Development', 10, order=4)

    # CBECE Level 1
    add('CBECE Level 1', 'language_grade', 'Language Development', 48, order=1)
    add('CBECE Level 1', 'math_grade', 'Cognitive Development - Mathematics', 24, order=2)
    add('CBECE Level 1', 'science_grade', 'Cognitive Development - Science', 18, order=3)
    add('CBECE Level 1', 'psychomotor_grade', 'Psychomotor Development', 20, order=4)
    add('CBECE Level 1', 'social_emotional_grade', 'Social-Emotional Development', 14, order=5)
    add('CBECE Level 1', 'artistic_grade', 'Artistic Development', 10, order=6)

    # CBECE Level 2
    add('CBECE Level 2', 'arabic_grade', 'Arabic Language Development', 66, order=1)
    add('CBECE Level 2', 'language_grade', 'Language Development', 66, order=2)
    add('CBECE Level 2', 'math_grade', 'Cognitive Development - Mathematics', 48, order=3)
    add('CBECE Level 2', 'science_grade', 'Cognitive Development - Science', 38, order=4)
    add('CBECE Level 2', 'psychomotor_grade', 'Psychomotor Development', 40, order=5)
    add('CBECE Level 2', 'social_emotional_grade', 'Social-Emotional Development', 40, order=6)
    add('CBECE Level 2', 'artistic_grade', 'Artistic Development', 16, order=7)

    # CBECE Level 3
    add('CBECE Level 3', 'arabic_grade', 'Arabic Language Development', 74, order=1)
    add('CBECE Level 3', 'language_grade', 'Language Development', 74, order=2)
    add('CBECE Level 3', 'math_grade', 'Cognitive Development - Mathematics', 50, order=3)
    add('CBECE Level 3', 'science_grade', 'Cognitive Development - Science', 38, order=4)
    add('CBECE Level 3', 'psychomotor_grade', 'Psychomotor Development', 42, order=5)
    add('CBECE Level 3', 'social_emotional_grade', 'Social-Emotional Development', 40, order=6)
    add('CBECE Level 3', 'artistic_grade', 'Artistic Development', 16, order=7)

    rs_7_9 = ['RS Grade 7', 'RS Grade 8', 'RS Grade 9', 'YFS Level 1 - RS Grade 9', 'YFS Level 2 - RS Grade 9']
    for p in rs_7_9:
        add(p, 'arabic_grade', 'Arabic Language', 20, order=1)
        add(p, 'language_grade', 'Foreign Language', 20, order=2)
        add(p, 'math_grade', 'Mathematics', 20, order=3)
        add(p, 'biology_grade', 'Biology', 20, order=4)
        add(p, 'chemistry_grade', 'Chemistry', 20, order=5)
        add(p, 'physics_grade', 'Physics', 20, order=6)

    rs_1_6 = ['RS Grade 1', 'RS Grade 2', 'RS Grade 3', 'RS Grade 4', 'RS Grade 5', 'RS Grade 6']
    for p in rs_1_6:
        add(p, 'arabic_grade', 'Arabic Language', 20, order=1)
        add(p, 'language_grade', 'Foreign Language', 20, order=2)
        add(p, 'math_grade', 'Mathematics', 20, order=3)
        add(p, 'science_grade', 'Science', 20, order=4)

    # Youth Scoring forms
    add('YBLN Level 1', 'arabic_grade', 'Arabic Language Development', 12, order=1, form_type='youth')
    add('YBLN Level 1', 'math_grade', 'Mathematics', 15, order=2, form_type='youth')
    add('YBLN Level 1', 'life_skills', 'Life Skills Development', 12, order=3, form_type='youth')

    add('YBLN Level 2', 'arabic_grade', 'Arabic Language Development', 12, order=1, form_type='youth')
    add('YBLN Level 2', 'language_grade', 'Foreign Language Development', 12, order=2, form_type='youth')
    add('YBLN Level 2', 'math_grade', 'Mathematics', 21, order=3, form_type='youth')
    add('YBLN Level 2', 'life_skills', 'Life Skills Development', 12, order=4, form_type='youth')

    yfs = ['YFS Level 1', 'YFS Level 2', 'YFS Level 1 - RS Grade 9', 'YFS Level 2 - RS Grade 9']
    for p in yfs:
        add(p, 'english_development', 'English Development', 100, order=1, form_type='youth')
        add(p, 'financial_development', 'Financial Literacy Development', 100, order=2, form_type='youth')
        add(p, 'it_development', 'IT Development', 100, order=3, form_type='youth')

def reverse_populate(apps, schema_editor):
    EducationProgrammeGrading = apps.get_model('mscc', 'EducationProgrammeGrading')
    EducationProgrammeGrading.objects.all().delete()

class Migration(migrations.Migration):

    dependencies = [
        ('mscc', '0009_education_programme_grading'),
    ]

    operations = [
        migrations.RunPython(populate_gradings, reverse_populate),
    ]
