from student_registration.child.models import Child
from student_registration.mscc.models import Registration, Teacher, EducationService, ExceptionalExam
from student_registration.alp.models import ALPRegistration, ALPTeacher, ALPGrading
from student_registration.attendances.models import MSCCAttendanceChild
from student_registration.alp.models import ALPAttendanceChild
names = ['رامي', 'كريم', 'ليان', 'جنى', 'خليل']
kids = Child.objects.filter(first_name__in=names)
regs = Registration.objects.filter(child__in=kids); aregs = ALPRegistration.objects.filter(child__in=kids)
MSCCAttendanceChild.objects.filter(registration__in=regs).delete(); ALPAttendanceChild.objects.filter(registration__in=aregs).delete()
ALPGrading.objects.filter(registration__in=aregs).delete()
try: ExceptionalExam.objects.filter(registration__in=regs).delete()
except Exception as e: print('exam', e)
EducationService.objects.filter(registration__in=regs).delete()
print('del regs', regs.delete(), aregs.delete(), 'kids', kids.delete())
print('teachers', Teacher.objects.filter(first_name__in=['Lina', 'لينا']).delete(), ALPTeacher.objects.filter(first_name__in=['Lina', 'لينا']).delete())
