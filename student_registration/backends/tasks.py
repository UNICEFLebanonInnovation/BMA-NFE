__author__ = 'achamseddine'

import time
import tablib
import logging
from django.utils.translation import gettext as _
from import_export.formats import base_formats
from student_registration.taskapp.celery import app
from .file import store_file
from openpyxl import load_workbook
from student_registration.backends.djqscsv import render_to_csv_response

logger = logging.getLogger(__name__)


@app.task
def export_attendance(params=None, return_data=False):
    from student_registration.attendances.models import Attendance

    queryset = Attendance.objects.all()

    if 'school' in params:
        queryset = queryset.filter(school_id=params['school'])
    if 'date' in params:
        queryset = queryset.filter(attendance_date=params['date'])
    if 'from_date' in params:
        queryset = queryset.filter(attendance_date__gte=params['from_date'])
    if 'to_date' in params:
        queryset = queryset.filter(attendance_date__lte=params['to_date'])
    if 'gov' in params:
        queryset = queryset.filter(school__location__parent=int(params['gov']))
    if 'school_type' in params:
        school_type = params['school_type']
        queryset = queryset.filter(school_type=school_type)
        if school_type == 'ALP':
            queryset = queryset.filter(alp_round__current_round=True)
        if school_type == '2nd-shift':
            queryset = queryset.filter(education_year__current_year=True)

    data = tablib.Dataset()

    data.headers = [
        _('School number'),
        _('School'),
        _('School type'),
        _('Education year/ALP round'),
        _('District'),
        _('Governorate'),

        _('Attendance date'),
        _('Validation status'),
        _('Validation date'),
        _('Validated by'),
        _('Close reason'),
        _('Exam day'),

        _('Level'),
        _('Section'),

        _('Student fullname'),
        _('Sex'),
        _('Age'),
        _('Attendance status'),
        _('Absence reason'),
        _('Dropout')
    ]

    content = []
    for line in queryset:
        school = line.school
        school_location = school.location
        school_location_parent = school_location.parent
        education_year = line.education_year
        alp_round = line.alp_round
        if not line.students:
            continue
        for level_section in line.students:
            attendances = line.students[level_section]
            students = attendances['students']
            for student in students:
                content = [
                    school.number,
                    school.name,
                    line.school_type,
                    education_year.name if education_year else alp_round.name,
                    school_location.name,
                    school_location_parent.name,

                    line.attendance_date,
                    line.validation_date,
                    line.validation_status,
                    line.validation_owner.username if line.validation_owner else '',
                    line.close_reason,
                    attendances['exam_day'],

                    student['level_name'],
                    student['section_name'],

                    student['student_fullname'],
                    student['student_sex'],
                    student['student_age'],
                    student['status'],
                    student['absence_reason'] if 'absence_reason' in student else '',
                    student['dropout'] if 'dropout' in student else '',
                ]
                data.append(content)

    timestamp = '{}-{}'.format('attendance', time.time())
    file_format = base_formats.XLSX()
    data = file_format.export_data(data)
    if return_data:
        return data
    store_file(data, timestamp)
    return True


@app.task
def import_attendance_by_student():
    from student_registration.attendances.models import Absentee
    wb = load_workbook(filename='attendance_by_student.xlsx', read_only=True)
    ws = wb['students']
    ctr = 0

    for row in ws.rows:
        try:
            if row[0].value == 'school_id':
                continue

            instance = Absentee.objects.create(
                school_id=row[0].value,
                student_id=row[6].value,
                education_year_id=row[1].value,
                level_name=row[2].value,
                level=row[3].value,
                section_name=row[4].value,
                section=row[5].value,
                attended_days=row[8].value,
                total_attended_days=row[9].value,
                absent_days=row[11].value,
                total_absent_days=row[12].value,
            )

            if not row[7].value == 'None':
                instance.last_attendance_date = row[7].value

            if not row[10].value == 'None':
                instance.last_absent_date = row[10].value

            if not row[13].value == 'None':
                instance.last_modification_date=row[13].value

            instance.save()

        except Exception as ex:
            pass
    logger.info(ctr)


@app.task
def export_attendance_by_student(params=None, return_data=False):
    from student_registration.attendances.models import Absentee

    queryset = Absentee.objects.all()

    data = tablib.Dataset()

    data.headers = [

        'school_id',
        'school_number',
        'school_name',
        'governorate',
        'district',
        'education_year/alp_round',
        'education_year_id',
        'alp_round_id',
        'level_name',
        'level',
        'section_name',
        'section',
        'student_id',
        'student_first_name',
        'student_father_name',
        'student_last_name',
        'student_mother_fullname',
        'student_sex',
        'student_age',
        'last_attendance_date',
        'attended_days',
        'total_attended_days',
        'last_absent_date',
        'absent_days',
        'total_absent_days',
        'last_modification_date',
    ]

    content = []
    for line in queryset:
        school = line.school
        school_location = school.location
        school_location_parent = school_location.parent
        education_year = line.education_year
        alp_round = line.alp_round

        if not education_year:
            continue

        content = [
            school.id,
            school.number,
            school.name,
            school_location_parent.name,
            school_location.name,
            education_year.name,
            education_year.id if education_year else '',
            alp_round.id if alp_round else '',
            line.level_name,
            line.level,
            line.section_name,
            line.section,
            line.student_id,
            line.student.first_name,
            line.student.father_name,
            line.student.last_name,
            line.student.mother_fullname,
            line.student.sex,
            line.student.age,
            line.last_attendance_date,
            line.attended_days,
            line.total_attended_days,
            line.last_absent_date,
            line.absent_days,
            line.total_absent_days,
            line.last_modification_date
        ]
        data.append(content)

    timestamp = '{}-{}'.format('attendance_by_student', time.time())
    file_format = base_formats.XLSX()
    data = file_format.export_data(data)
    if return_data:
        return data
    store_file(data, timestamp)
    return True


@app.task
def export_last_attendance(params=None, return_data=False):
    from student_registration.attendances.tasks import calculate_last_attendance_date
    from student_registration.enrollments.models import Enrollment

    calculate_last_attendance_date()
    title = 'Last_Attendance'

    queryset = Enrollment.objects.filter(education_year__current_year=True)

    headers = {
        'school__number': _('School number'),
        'school__name': _('School'),
        'school__location__name': _('District'),
        'school__location__parent__name': _('Governorate'),
        'student__number': 'student number',
        'student__first_name': _('Student first name'),
        'student__father_name': _('Student father name'),
        'student__last_name': _('Student last name'),
        'student__mother_fullname': _('Mother fullname'),
        'student__sex': _('Sex'),
        'student__birthday_year': _('year'),
        'student__birthday_month': _('month'),
        'student__birthday_day': _('day'),
        'student__place_of_birth': _('Place of birth'),
        'student__phone': _('Phone number'),
        'student__phone_prefix': _('Phone prefix'),

        'student__id_number': _('Student ID Number'),
        'student__nationality__name': _('Student nationality'),

        'section__name': _('Current Section'),
        'classroom__name': _('Current Class'),

        'last_attendance_date': _('Last attendance date'),
        'last_absent_date': _('Last absent date'),

    }

    queryset = queryset.values(
        'school__number',
        'school__name',
        'school__location__name',
        'school__location__parent__name',
        'student__number',
        'student__first_name',
        'student__father_name',
        'student__last_name',
        'student__mother_fullname',
        'student__sex',
        'student__birthday_year',
        'student__birthday_month',
        'student__birthday_day',
        'student__place_of_birth',
        'student__phone',
        'student__phone_prefix',

        'student__id_number',
        'student__nationality__name',

        'section__name',
        'classroom__name',

        'last_attendance_date',
        'last_absent_date',

    )

    return render_to_csv_response(queryset, field_header_map=headers)

