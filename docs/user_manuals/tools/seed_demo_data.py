import datetime, random
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from student_registration.locations.models import Location, LocationType, Center
from student_registration.schools.models import PartnerOrganization, School, Section
from student_registration.students.models import Nationality, IDType
from student_registration.clm.models import Disability
from student_registration.child.models import Child
from student_registration.mscc.models import Round, RoundPartner, Registration, Teacher
from student_registration.alp.models import ALPRound, ALPProgram, ALPRegistration, ALPTeacher, ALPGradingDefinition

random.seed(7)
User = get_user_model()

gov_t, _ = LocationType.objects.get_or_create(pk=1, defaults={'name': 'Governorate'})
dis_t, _ = LocationType.objects.get_or_create(pk=2, defaults={'name': 'District'})
cad_t, _ = LocationType.objects.get_or_create(pk=3, defaults={'name': 'Cadaster'})

def loc(name, name_en, t, parent=None):
    obj, _ = Location.objects.get_or_create(name=name, type=t, parent=parent, defaults={'name_en': name_en})
    return obj

beirut = loc('بيروت', 'Beirut', gov_t)
beirut_d = loc('بيروت', 'Beirut', dis_t, beirut)
ras = loc('رأس بيروت', 'Ras Beirut', cad_t, beirut_d)
ach = loc('الأشرفية', 'Achrafieh', cad_t, beirut_d)
maz = loc('المزرعة', 'Mazraa', cad_t, beirut_d)
ml = loc('جبل لبنان', 'Mount Lebanon', gov_t)
metn = loc('المتن', 'Metn', dis_t, ml)
jd = loc('الجديدة', 'Jdeideh', cad_t, metn)
bh = loc('برج حمود', 'Bourj Hammoud', cad_t, metn)
baabda = loc('بعبدا', 'Baabda', dis_t, ml)
chiyah = loc('الشياح', 'Chiyah', cad_t, baabda)
hadath = loc('الحدث', 'Hadath', cad_t, baabda)
north = loc('الشمال', 'North Lebanon', gov_t)
tripoli = loc('طرابلس', 'Tripoli', dis_t, north)
mina = loc('الميناء', 'Mina', cad_t, tripoli)

nats = {}
for pk, ar, en, code in [(1, 'لبناني', 'Lebanese', 'LB'), (2, 'سوري', 'Syrian', 'SY'), (3, 'فلسطيني', 'Palestinian', 'PS'), (4, 'عراقي', 'Iraqi', 'IQ'), (6, 'غير ذلك', 'Other', 'OT')]:
    nats[en], _ = Nationality.objects.get_or_create(pk=pk, defaults={'name': ar, 'name_en': en, 'code': code})

diss = {}
for ar, en in [('لا يوجد', 'None'), ('إعاقة بصرية', 'Visual impairment'), ('إعاقة سمعية', 'Hearing impairment'), ('إعاقة حركية', 'Physical disability'), ('إعاقة ذهنية', 'Intellectual disability'), ('غير ذلك', 'Other')]:
    diss[en], _ = Disability.objects.get_or_create(name=ar, defaults={'name_en': en})

for n in ['UNHCR Registration Certificate', 'Lebanese ID', 'Syrian ID', 'Palestinian ID', 'Birth Certificate', 'Passport', 'No ID']:
    IDType.objects.get_or_create(name=n, defaults={'active': True})

partner, _ = PartnerOrganization.objects.get_or_create(name='Demo Partner NGO', defaults={'short_name': 'DPN'})
partner2, _ = PartnerOrganization.objects.get_or_create(name='Second Partner NGO', defaults={'short_name': 'SPN'})
center, _ = Center.objects.get_or_create(name='Beirut Learning Center', defaults=dict(partner=partner, governorate=beirut, caza=beirut_d, cadaster=ras, type='Community Hub', longitude=35.4800, latitude=33.8960))
center2, _ = Center.objects.get_or_create(name='Metn Community Center', defaults=dict(partner=partner, governorate=ml, caza=metn, cadaster=jd, type='Municipality', longitude=35.5700, latitude=33.8900))
center3, _ = Center.objects.get_or_create(name='Tripoli Youth Hub', defaults=dict(partner=partner2, governorate=north, caza=tripoli, cadaster=mina, type='Community Hub', longitude=35.8300, latitude=34.4400))

rnd_old, _ = Round.objects.get_or_create(name='Round 2024-2025', defaults={'current_year': False, 'year': 2024})
rnd, _ = Round.objects.get_or_create(name='Round 2025-2026', defaults={'current_year': True, 'year': 2025})
for p in (partner, partner2):
    RoundPartner.objects.get_or_create(round=rnd, partner=p, defaults={'start_date': datetime.date(2025, 10, 1), 'end_date': datetime.date(2026, 6, 30)})

groups = {n: Group.objects.get_or_create(name=n)[0] for n in ['MSCC', 'MSCC_CENTER', 'MSCC_PARTNER', 'MSCC_UNICEF', 'ALP_SCHOOL', 'EXPORT']}

def mkuser(username, pw, grp, **kw):
    u, created = User.objects.get_or_create(username=username, defaults=kw)
    for k, v in kw.items():
        setattr(u, k, v)
    u.set_password(pw); u.save()
    u.groups.set([groups[g] for g in grp])
    return u

PW = 'Nfe@Demo2026!'
nfe_user = mkuser('nfe.center', PW, ['MSCC', 'MSCC_CENTER', 'EXPORT'], first_name='Rania', last_name='Haddad', center=center, partner=partner, email='rania@example.org')
partner_user = mkuser('nfe.partner', PW, ['MSCC_PARTNER'], first_name='Partner', last_name='User', partner=partner)

school, _ = School.objects.get_or_create(number='1234', defaults=dict(name='Beirut Public School - Demo', type='Public', operating_shift='Afternoon', director_name='Dr. Samir Khoury', land_phone_number='01-123456', email='school1234@example.org', is_bma=True))
alp_user = mkuser('alp.school', PW, ['ALP_SCHOOL'], first_name='Nadia', last_name='Saleh', school=school, email='nadia@example.org')
admin = mkuser('admin', 'Admin@Demo2026!', [], is_staff=True, is_superuser=True)

alp_rnd_old, _ = ALPRound.objects.get_or_create(name='2024-2025', defaults={'current_year': False})
alp_rnd, _ = ALPRound.objects.get_or_create(name='2025-2026', defaults={'current_year': True})
progs = {n: ALPProgram.objects.get_or_create(name=n)[0] for n in ['ALP Level 1', 'ALP Level 2', 'ALP Level 3']}
secs = {n: Section.objects.get_or_create(name=n)[0] for n in ['A', 'B', 'C']}
for m in ['Arabic', 'English', 'Mathematics', 'Science']:
    ALPGradingDefinition.objects.get_or_create(material=m, defaults={'min_grade': 0, 'max_grade': 20})

BOYS = [('أحمد', 'Ahmad'), ('محمد', 'Mohamad'), ('علي', 'Ali'), ('حسن', 'Hassan'), ('عمر', 'Omar'), ('خالد', 'Khaled'), ('يوسف', 'Youssef'), ('كريم', 'Karim')]
GIRLS = [('فاطمة', 'Fatima'), ('مريم', 'Mariam'), ('سارة', 'Sara'), ('نور', 'Nour'), ('ليلى', 'Layla'), ('هبة', 'Hiba'), ('رنا', 'Rana'), ('زينب', 'Zeinab')]
FATHERS = ['Mahmoud', 'Ibrahim', 'Hussein', 'Samir', 'Walid', 'Bassam', 'Nabil', 'Fadi']
FAMILIES = ['Al Hassan', 'Khalil', 'Saad', 'Al Ahmad', 'Mansour', 'Haidar', 'Al Masri', 'Darwish']
MOTHERS = ['Amal Khalil', 'Huda Saad', 'Rima Mansour', 'Salma Haidar', 'Maha Darwish', 'Dalal Nasser', 'Hanan Fares', 'Lina Aoun']

def mkchild(i, places):
    gender = 'Male' if i % 2 == 0 else 'Female'
    name = (BOYS if gender == 'Male' else GIRLS)[i % 8][1]
    gov, dist, cad = random.choice(places)
    nat = random.choice(['Syrian', 'Syrian', 'Lebanese', 'Palestinian'])
    year = random.choice(range(2011, 2018))
    c = Child.objects.create(
        first_name=name, father_name=FATHERS[i % 8], last_name=FAMILIES[(i * 3) % 8], mother_fullname=MOTHERS[(i * 5) % 8],
        gender=gender, nationality=nats[nat], birthday_year=str(year), birthday_month=str(random.randint(1, 12)), birthday_day=str(random.randint(1, 28)),
        governorate=gov, district=dist, cadaster=cad, village=cad.name_en, country_of_birth='LB' if nat == 'Lebanese' else 'SY',
        place_of_birth='Beirut' if nat == 'Lebanese' else 'Aleppo', disability=diss['None'] if i % 5 else diss['Physical disability'],
        first_phone_number='03' + str(100000 + i * 7919), first_phone_owner='Father',
    )
    return c

beirut_places = [(beirut, beirut_d, ras), (beirut, beirut_d, ach), (beirut, beirut_d, maz)]
metn_places = [(ml, metn, jd), (ml, metn, bh)]

if not Registration.objects.exists():
    for i in range(14):
        c = mkchild(i, beirut_places)
        Registration.objects.create(child=c, center=center, partner=partner, round=rnd, nfe_programme=random.choice(['BLN Level 1', 'BLN Level 2', 'BLN Level 3']), owner=nfe_user, modified_by=nfe_user)
    for i in range(6):
        c = mkchild(i + 20, metn_places)
        Registration.objects.create(child=c, center=center2, partner=partner, round=rnd, nfe_programme=random.choice(['BLN Level 1', 'BLN Level 2']), owner=nfe_user, modified_by=nfe_user)

if not ALPRegistration.objects.exists():
    for i in range(10):
        c = mkchild(i + 40, beirut_places)
        ALPRegistration.objects.create(child=c, school=school, round=alp_rnd, programme=progs[['ALP Level 1', 'ALP Level 2', 'ALP Level 3'][i % 3]], section=secs['A' if i % 2 else 'B'],
                                       registration_date=datetime.date(2025, 10, 1) + datetime.timedelta(days=i * 2), have_labour='No',
                                       source_of_identification='BLN programme', owner=alp_user, modified_by=alp_user)

if not Teacher.objects.exists():
    for fn, fa, ln, mo, sex in [('Hala', 'Youssef', 'Nasr', 'Mona Khoury', 'Female'), ('Jad', 'Elias', 'Saba', 'Rita Saba', 'Male'), ('Maya', 'Karim', 'Farah', 'Nada Farah', 'Female')]:
        t = Teacher(first_name=fn, father_name=fa, last_name=ln, mother_fullname=mo, sex=sex, birthdate=datetime.date(1990, 5, 10), id_number='LB' + str(random.randint(100000, 999999)),
                    id_type=IDType.objects.get(name='Lebanese ID'), nationality=nats['Lebanese'])
        for f, v in [('partner', partner), ('center', center), ('owner', nfe_user)]:
            if hasattr(t, f): setattr(t, f, v)
        t.save()

if not ALPTeacher.objects.exists():
    for fn, fa, ln, mo, sex in [('Rami', 'Nabil', 'Chehab', 'Siham Chehab', 'Male'), ('Dalia', 'Fouad', 'Azar', 'Nahla Azar', 'Female')]:
        ALPTeacher.objects.create(first_name=fn, father_name=fa, last_name=ln, mother_fullname=mo, sex=sex, birthdate=datetime.date(1988, 3, 15), id_number='LB' + str(random.randint(100000, 999999)),
                                  id_type=IDType.objects.get(name='Lebanese ID'), nationality=nats['Lebanese'], round=alp_rnd, school=school, email=fn.lower() + '@example.org', phone_number='03123456',
                                  teacher_assignment='ALP teacher', teaching_hours_private_school=10, teaching_hours_mscc=0, years_of_experience=6, owner=alp_user)

print('SEED OK', Registration.objects.count(), ALPRegistration.objects.count(), Teacher.objects.count(), ALPTeacher.objects.count())
