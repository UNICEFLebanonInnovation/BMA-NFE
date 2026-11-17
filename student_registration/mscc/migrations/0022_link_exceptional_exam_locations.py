"""Preserve exam residence codes while linking existing Location records."""

import re
import unicodedata

import django.db.models.deletion
from django.db import migrations, models


# Freeze the original 0021 choices: future catalog changes must not change this
# conversion or its rollback. Names match exactly after separator normalization.
RESIDENCES = {
    'beirut': ('Beirut / بيروت', {'beirut': 'Beirut / بيروت'}),
    'mount_lebanon': ('Mount Lebanon / جبل لبنان', {
        'baabda': 'Baabda / بعبدا', 'metn': 'Metn / المتن',
        'keserwan': 'Keserwan / كسروان', 'jbeil': 'Jbeil / جبيل',
        'aley': 'Aley / عاليه', 'chouf': 'Chouf / الشوف',
    }),
    'north_lebanon': ('North Lebanon / الشمال', {
        'tripoli': 'Tripoli / طرابلس',
        'minnieh_dannieh': 'Minniyeh–Danniyeh / المنية–الضنية',
        'zgharta': 'Zgharta / زغرتا', 'koura': 'Koura / الكورة',
        'bcharre': 'Bcharre / بشري', 'batroun': 'Batroun / البترون',
    }),
    'akkar': ('Akkar / عكار', {'akkar': 'Akkar / عكار'}),
    'bekaa': ('Bekaa / البقاع', {
        'zahle': 'Zahle / زحلة', 'west_bekaa': 'West Bekaa / البقاع الغربي',
        'rashaya': 'Rashaya / راشيا',
    }),
    'baalbek_hermel': ('Baalbek–Hermel / بعلبك–الهرمل', {
        'baalbek': 'Baalbek / بعلبك', 'hermel': 'Hermel / الهرمل',
    }),
    'south_lebanon': ('South Lebanon / الجنوب', {
        'sidon': 'Sidon / صيدا', 'tyre': 'Tyre / صور', 'jezzine': 'Jezzine / جزين',
    }),
    'nabatieh': ('Nabatieh / النبطية', {
        'nabatieh': 'Nabatieh / النبطية', 'bint_jbeil': 'Bint Jbeil / بنت جبيل',
        'marjayoun': 'Marjayoun / مرجعيون', 'hasbaya': 'Hasbaya / حاصبيا',
    }),
}
GOVERNORATE_ALIASES = {
    'beirut': ('Beirut', 'بيروت'),
    'mount_lebanon': ('Mount Lebanon', 'جبل لبنان'),
    'north_lebanon': ('North', 'North Lebanon', 'الشمال', 'لبنان الشمالي'),
    'akkar': ('Akkar', 'عكار'),
    'bekaa': ('Bekaa', 'Beqaa', 'البقاع'),
    'baalbek_hermel': ('Baalbek Hermel', 'Baalbek El Hermel', 'بعلبك الهرمل'),
    'south_lebanon': ('South', 'South Lebanon', 'الجنوب', 'لبنان الجنوبي'),
    'nabatieh': ('Nabatieh', 'النبطية'),
}
GOVERNORATE_CHOICES = [(code, row[0]) for code, row in RESIDENCES.items()]
DISTRICT_CHOICES = list(dict(
    (code, label) for _, districts in RESIDENCES.values()
    for code, label in districts.items()
).items())


def _normalize(value):
    value = unicodedata.normalize('NFKC', str(value or '')).casefold()
    return re.sub(r'[\W_]+', ' ', value, flags=re.UNICODE).strip()


def _names(location):
    return {_normalize(value) for value in (location.name, location.name_en) if value}


def _label_names(code, label, aliases=None):
    return {
        _normalize(value) for value in label.split(' / ') + list((aliases or {}).get(code, ()))
    }


def _unique_code(location, labelled_codes, aliases=None):
    matches = [
        code for code, label in labelled_codes
        if _names(location).intersection(_label_names(code, label, aliases))
    ]
    return matches[0] if len(matches) == 1 else ''


def _restored_location(value, locations, location_type, parent_id=None):
    """Recover rollback names/identity markers without accepting wrong types."""
    marker = re.fullmatch(r'@location:([1-9]\d*)', str(value or ''))
    if marker:
        candidates = [row for row in locations if row.pk == int(marker.group(1))]
    else:
        name = _normalize(value)
        candidates = [row for row in locations if name and name in _names(row)]
    candidates = [
        row for row in candidates if row.type_id == location_type
        and (location_type != 2 or row.parent_id == parent_id)
    ]
    return candidates[0].pk if len(candidates) == 1 else None


def _rollback_value(location, code, historical_value):
    if code:
        return code
    if location:
        # A compact identity marker retains long Location names within the
        # original 64-character column and can be linked again on reapplication.
        return location.name if len(location.name) <= 64 else '@location:%s' % location.pk
    return historical_value or ''


def _forward_mappings(locations):
    """Only unambiguous original catalog codes can select existing records."""
    governorate_ids = {}
    district_ids = {}
    for code, (label, districts) in RESIDENCES.items():
        candidates = [
            location for location in locations if location.type_id == 1
            and _unique_code(location, GOVERNORATE_CHOICES, GOVERNORATE_ALIASES) == code
        ]
        if len(candidates) != 1:
            continue
        governorate_id = candidates[0].pk
        governorate_ids[code] = governorate_id
        for district_code, district_label in districts.items():
            candidates = [
                location for location in locations if location.type_id == 2
                and location.parent_id == governorate_id
                and _unique_code(location, districts.items()) == district_code
            ]
            if len(candidates) == 1:
                district_ids[(code, district_code)] = candidates[0].pk
    return governorate_ids, district_ids


def _residence_ids(governorate_value, district_value, locations, mappings):
    """The same typed, parent-aware resolver serves application and rollback."""
    governorate_ids, district_ids = mappings
    governorate_id = governorate_ids.get(governorate_value)
    if governorate_value not in RESIDENCES:
        governorate_id = _restored_location(governorate_value, locations, 1)
    if not governorate_id:
        return None, None
    district_id = district_ids.get((governorate_value, district_value))
    if governorate_value not in RESIDENCES or district_value not in dict(DISTRICT_CHOICES):
        district_id = _restored_location(district_value, locations, 2, parent_id=governorate_id)
    return governorate_id, district_id


def link_existing_residences(apps, schema_editor):
    Exam = apps.get_model('mscc', 'ExceptionalExam')
    Location = apps.get_model('locations', 'Location')
    db = schema_editor.connection.alias
    locations = list(Location.objects.using(db).filter(type_id__in=(1, 2)))
    mappings = _forward_mappings(locations)

    for exam in Exam.objects.using(db).all().iterator():
        governorate_id, district_id = _residence_ids(
            exam.governorate_legacy, exam.district_legacy, locations, mappings,
        )
        if governorate_id:
            Exam.objects.using(db).filter(pk=exam.pk).update(
                governorate_id=governorate_id,
                district_id=district_id,
            )


def restore_residence_codes(apps, schema_editor):
    Exam = apps.get_model('mscc', 'ExceptionalExam')
    Location = apps.get_model('locations', 'Location')
    db = schema_editor.connection.alias
    locations = {row.pk: row for row in Location.objects.using(db).filter(type_id__in=(1, 2))}
    location_rows = list(locations.values())
    mappings = _forward_mappings(location_rows)
    for exam in Exam.objects.using(db).all().iterator():
        governorate = locations.get(exam.governorate_id)
        district = locations.get(exam.district_id)
        governorate_code = ''
        if governorate and governorate.type_id == 1:
            matches = [
                code for code, (label, _) in RESIDENCES.items()
                if _names(governorate).intersection(_label_names(code, label, GOVERNORATE_ALIASES))
            ]
            if len(matches) == 1:
                governorate_code = matches[0]
        restored_governorate = _rollback_value(
            governorate, governorate_code, exam.governorate_legacy,
        )
        # A readable catalog code/name is suitable only when reapplying the
        # forward migration selects the exact same record. Duplicate names and
        # older governorate boundaries otherwise require an identity marker.
        restored_governorate_id, _ = _residence_ids(
            restored_governorate, '', location_rows, mappings,
        )
        if governorate and governorate.type_id == 1 and restored_governorate_id != governorate.pk:
            restored_governorate = '@location:%s' % governorate.pk
        district_code = ''
        if (governorate_code and district and district.type_id == 2
                and district.parent_id == governorate.pk):
            matches = [
                code for code, label in RESIDENCES[governorate_code][1].items()
                if _names(district).intersection(_label_names(code, label))
            ]
            if len(matches) == 1:
                district_code = matches[0]
        restored_district = _rollback_value(district, district_code, exam.district_legacy)
        _, restored_district_id = _residence_ids(
            restored_governorate, restored_district, location_rows, mappings,
        )
        if (governorate and district and district.type_id == 2
                and district.parent_id == governorate.pk and restored_district_id != district.pk):
            restored_district = '@location:%s' % district.pk
        Exam.objects.using(db).filter(pk=exam.pk).update(
            governorate_legacy=restored_governorate,
            district_legacy=restored_district,
        )


class Migration(migrations.Migration):
    dependencies = [
        ('mscc', '0021_exceptional_exam'),
        ('locations', '0003_alter_location_options'),
    ]

    operations = [
        migrations.RenameField('exceptionalexam', 'governorate', 'governorate_legacy'),
        migrations.RenameField('exceptionalexam', 'district', 'district_legacy'),
        migrations.AlterField(
            model_name='exceptionalexam', name='governorate_legacy',
            field=models.CharField(blank=True, null=True, choices=GOVERNORATE_CHOICES,
                                   max_length=64, verbose_name='Legacy governorate / المحافظة السابقة'),
        ),
        migrations.AlterField(
            model_name='exceptionalexam', name='district_legacy',
            field=models.CharField(blank=True, null=True, choices=DISTRICT_CHOICES,
                                   max_length=64, verbose_name='Legacy district / القضاء السابق'),
        ),
        migrations.AddField(
            model_name='exceptionalexam', name='governorate',
            field=models.ForeignKey(
                blank=True, null=True, limit_choices_to={'type_id': 1},
                on_delete=django.db.models.deletion.SET_NULL, related_name='+',
                to='locations.location', verbose_name='Governorate / المحافظة',
            ),
        ),
        migrations.AddField(
            model_name='exceptionalexam', name='district',
            field=models.ForeignKey(
                blank=True, null=True, limit_choices_to={'type_id': 2},
                on_delete=django.db.models.deletion.SET_NULL, related_name='+',
                to='locations.location', verbose_name='District/Caza / القضاء',
            ),
        ),
        migrations.AlterField(
            model_name='exceptionalexam', name='nearest_town',
            field=models.CharField(
                choices=[('achrafieh', 'Achrafieh / الأشرفية'), ('moussaitbeh', 'Moussaitbeh / المصيطبة'), ('ras_beirut', 'Ras Beirut / رأس بيروت'), ('mazraa', 'Mazraa / المزرعة'), ('medawar', 'Medawar / المدور'), ('minet_el_hosn', 'Minet El Hosn / ميناء الحصن'), ('zokak_el_blat', 'Zokak El Blat / زقاق البلاط'), ('baabda', 'Baabda / بعبدا'), ('hadath', 'Hadath / الحدث'), ('hazmieh', 'Hazmieh / الحازمية'), ('chiyah', 'Chiyah / الشياح'), ('furn_el_chebbak', 'Furn El Chebbak / فرن الشباك'), ('kfarshima', 'Kfarshima / كفرشيما'), ('aley', 'Aley / عاليه'), ('jdeideh', 'Jdeideh / الجديدة'), ('bouchrieh', 'Bouchrieh / البوشرية'), ('sed_el_bouchrieh', 'Sed El Bouchrieh / سد البوشرية'), ('bourj_hammoud', 'Bourj Hammoud / برج حمود'), ('antelias', 'Antelias / أنطلياس'), ('jal_el_dib', 'Jal El Dib / جل الديب'), ('bikfaya', 'Bikfaya / بكفيا'), ('broummana', 'Broummana / برمانا'), ('jounieh', 'Jounieh / جونية'), ('ghazir', 'Ghazir / غزير'), ('zouk_mikael', 'Zouk Mikael / ذوق مكايل'), ('zouk_mosbeh', 'Zouk Mosbeh / ذوق مصبح'), ('ajaltoun', 'Ajaltoun / عجلتون'), ('faraya', 'Faraya / فاريا'), ('jbeil', 'Jbeil / جبيل'), ('amchit', 'Amchit / عمشيت'), ('halat', 'Halat / حالات'), ('qartaba', 'Qartaba / قرطبا'), ('lassa', 'Lassa / لاسا'), ('bhamdoun', 'Bhamdoun / بحمدون'), ('souq_el_gharb', 'Souq El Gharb / سوق الغرب'), ('aramoun', 'Aramoun / عرمون'), ('bchamoun', 'Bchamoun / بشامون'), ('choueifat', 'Choueifat / شويفات'), ('beit_eddine', 'Beit Eddine / بيت الدين'), ('deir_el_qamar', 'Deir El Qamar / دير القمر'), ('baakline', 'Baakline / بعقلين'), ('moukhtara', 'Moukhtara / المختارة'), ('barja', 'Barja / برجا'), ('chhim', 'Chhim / شحيم'), ('damour', 'Damour / الدامور'), ('tripoli', 'Tripoli / طرابلس'), ('el_mina', 'El Mina / الميناء'), ('qobbeh', 'Qobbeh / القبة'), ('abi_samra', 'Abi Samra / أبي سمراء'), ('tebbaneh', 'Tebbaneh / التبانة'), ('minnieh', 'Minniyeh / المنية'), ('bhanine', 'Bhanine / بحنين'), ('deir_ammar', 'Deir Ammar / دير عمار'), ('sir_el_dannieh', 'Sir El Danniyeh / سير الضنية'), ('bakhoun', 'Bakhoun / بخعون'), ('zgharta', 'Zgharta / زغرتا'), ('ehden', 'Ehden / إهدن'), ('rachine', 'Rachine / رشعين'), ('amioun', 'Amioun / أميون'), ('anfeh', 'Anfeh / أنفه'), ('kousba', 'Kousba / كوسبا'), ('kfar_aaqqa', 'Kfar Aaqqa / كفرعقا'), ('bcharre', 'Bcharre / بشري'), ('hadath_el_jebbeh', 'Hadath El Jebbeh / حدث الجبة'), ('bqaa_kafra', 'Bqaa Kafra / بقاعكفرا'), ('batroun', 'Batroun / البترون'), ('chekka', 'Chekka / شكا'), ('tannourine', 'Tannourine / تنورين'), ('kfar_aabida', 'Kfar Aabida / كفرعبيدا'), ('halba', 'Halba / حلبا'), ('qoubaiyat', 'Qoubaiyat / القبيات'), ('bebnine', 'Bebnine / ببنين'), ('abdeh', 'Abdeh / العبدة'), ('wadi_khaled', 'Wadi Khaled / وادي خالد'), ('berqayel', 'Berqayel / برقايل'), ('mishmish', 'Mishmish / مشمش'), ('zahle', 'Zahle / زحلة'), ('taanayel', 'Taanayel / تعنايل'), ('chtoura', 'Chtoura / شتورا'), ('qabb_elias', 'Qabb Elias / قب إلياس'), ('bar_elias', 'Bar Elias / بر الياس'), ('majdal_anjar', 'Majdal Anjar / مجدل عنجر'), ('joub_jannine', 'Joub Jannine / جب جنين'), ('qaraoun', 'Qaraoun / القرعون'), ('machghara', 'Machghara / مشغرة'), ('sohmor', 'Sohmor / سحمر'), ('gaza', 'Gaza / غزة'), ('rashaya', 'Rashaya / راشيا'), ('kfar_mechki', 'Kfar Mechki / كفرمشكي'), ('bakka', 'Bakka / بكا'), ('baalbek', 'Baalbek / بعلبك'), ('douris', 'Douris / دورس'), ('arsal', 'Arsal / عرسال'), ('labweh', 'Labweh / اللبوة'), ('nabi_chit', 'Nabi Chit / النبي شيت'), ('chmistar', 'Chmistar / شمسطار'), ('hermel', 'Hermel / الهرمل'), ('qasr', 'Qasr / القصر'), ('sidon', 'Sidon / صيدا'), ('abra', 'Abra / عبرا'), ('hlaliyeh', 'Hlaliyeh / الهلالية'), ('maghdoucheh', 'Maghdoucheh / مغدوشة'), ('ghazieh', 'Ghazieh / الغازية'), ('tyre', 'Tyre / صور'), ('abbassiyeh', 'Abbassiyeh / العباسية'), ('bourj_el_chamali', 'Bourj El Chamali / برج الشمالي'), ('qana', 'Qana / قانا'), ('jouaiya', 'Jouaiya / جويا'), ('naqoura', 'Naqoura / الناقورة'), ('jezzine', 'Jezzine / جزين'), ('bkassine', 'Bkassine / بكاسين'), ('lebaa', 'Lebaa / لبعا'), ('nabatieh', 'Nabatieh / النبطية'), ('kfar_roummane', 'Kfar Roummane / كفررمان'), ('habbouch', 'Habbouch / حبوش'), ('douair', 'Douair / الدوير'), ('bint_jbeil', 'Bint Jbeil / بنت جبيل'), ('tebnine', 'Tebnine / تبنين'), ('ainata', 'Ainata / عيناتا'), ('aitaroun', 'Aitaroun / عيترون'), ('rmeich', 'Rmeich / رميش'), ('marjayoun', 'Marjayoun / مرجعيون'), ('khiam', 'Khiam / الخيام'), ('kfar_kila', 'Kfar Kila / كفركلا'), ('adaisseh', 'Adaisseh / العديسة'), ('qlayaa', 'Qlayaa / القليعة'), ('hasbaya', 'Hasbaya / حاصبيا'), ('chebaa', 'Chebaa / شبعا'), ('kfar_chouba', 'Kfar Chouba / كفرشوبا'), ('hebbariyeh', 'Hebbariyeh / الهبارية')],
                max_length=100, verbose_name='Village / القرية',
            ),
        ),
        migrations.RunPython(link_existing_residences, restore_residence_codes),
    ]
