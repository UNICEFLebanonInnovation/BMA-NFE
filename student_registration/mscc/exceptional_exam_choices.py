"""Bilingual exceptional-exam choices from the supplied NFE MIS document.

Residence choices belong to this exam form, rather than the shared Location
model. Keep the document's parent relationships and Arabic spelling: a town
can appear under more than one district in the supplied table.
"""


RESIDENCE_CATALOG = {
    'beirut': {
        'label': 'Beirut / بيروت',
        'districts': {
            'beirut': {
                'label': 'Beirut / بيروت',
                'towns': (
                    ('achrafieh', 'Achrafieh / الأشرفية'),
                    ('moussaitbeh', 'Moussaitbeh / المصيطبة'),
                    ('ras_beirut', 'Ras Beirut / رأس بيروت'),
                    ('mazraa', 'Mazraa / المزرعة'),
                    ('medawar', 'Medawar / المدور'),
                    ('minet_el_hosn', 'Minet El Hosn / ميناء الحصن'),
                    ('zokak_el_blat', 'Zokak El Blat / زقاق البلاط'),
                ),
            },
        },
    },
    'mount_lebanon': {
        'label': 'Mount Lebanon / جبل لبنان',
        'districts': {
            'baabda': {
                'label': 'Baabda / بعبدا',
                'towns': (
                    ('baabda', 'Baabda / بعبدا'),
                    ('hadath', 'Hadath / الحدث'),
                    ('hazmieh', 'Hazmieh / الحازمية'),
                    ('chiyah', 'Chiyah / الشياح'),
                    ('furn_el_chebbak', 'Furn El Chebbak / فرن الشباك'),
                    ('kfarshima', 'Kfarshima / كفرشيما'),
                    ('aley', 'Aley / عاليه'),
                ),
            },
            'metn': {
                'label': 'Metn / المتن',
                'towns': (
                    ('jdeideh', 'Jdeideh / الجديدة'),
                    ('bouchrieh', 'Bouchrieh / البوشرية'),
                    ('sed_el_bouchrieh', 'Sed El Bouchrieh / سد البوشرية'),
                    ('bourj_hammoud', 'Bourj Hammoud / برج حمود'),
                    ('antelias', 'Antelias / أنطلياس'),
                    ('jal_el_dib', 'Jal El Dib / جل الديب'),
                    ('bikfaya', 'Bikfaya / بكفيا'),
                    ('broummana', 'Broummana / برمانا'),
                ),
            },
            'keserwan': {
                'label': 'Keserwan / كسروان',
                'towns': (
                    ('jounieh', 'Jounieh / جونية'),
                    ('ghazir', 'Ghazir / غزير'),
                    ('zouk_mikael', 'Zouk Mikael / ذوق مكايل'),
                    ('zouk_mosbeh', 'Zouk Mosbeh / ذوق مصبح'),
                    ('ajaltoun', 'Ajaltoun / عجلتون'),
                    ('faraya', 'Faraya / فاريا'),
                ),
            },
            'jbeil': {
                'label': 'Jbeil / جبيل',
                'towns': (
                    ('jbeil', 'Jbeil / جبيل'),
                    ('amchit', 'Amchit / عمشيت'),
                    ('halat', 'Halat / حالات'),
                    ('qartaba', 'Qartaba / قرطبا'),
                    ('lassa', 'Lassa / لاسا'),
                ),
            },
            'aley': {
                'label': 'Aley / عاليه',
                'towns': (
                    ('aley', 'Aley / عاليه'),
                    ('bhamdoun', 'Bhamdoun / بحمدون'),
                    ('souq_el_gharb', 'Souq El Gharb / سوق الغرب'),
                    ('aramoun', 'Aramoun / عرمون'),
                    ('bchamoun', 'Bchamoun / بشامون'),
                    ('choueifat', 'Choueifat / شويفات'),
                ),
            },
            'chouf': {
                'label': 'Chouf / الشوف',
                'towns': (
                    ('beit_eddine', 'Beit Eddine / بيت الدين'),
                    ('deir_el_qamar', 'Deir El Qamar / دير القمر'),
                    ('baakline', 'Baakline / بعقلين'),
                    ('moukhtara', 'Moukhtara / المختارة'),
                    ('barja', 'Barja / برجا'),
                    ('chhim', 'Chhim / شحيم'),
                    ('damour', 'Damour / الدامور'),
                ),
            },
        },
    },
    'north_lebanon': {
        'label': 'North Lebanon / الشمال',
        'districts': {
            'tripoli': {
                'label': 'Tripoli / طرابلس',
                'towns': (
                    ('tripoli', 'Tripoli / طرابلس'),
                    ('el_mina', 'El Mina / الميناء'),
                    ('qobbeh', 'Qobbeh / القبة'),
                    ('abi_samra', 'Abi Samra / أبي سمراء'),
                    ('tebbaneh', 'Tebbaneh / التبانة'),
                ),
            },
            'minnieh_dannieh': {
                'label': 'Minniyeh–Danniyeh / المنية–الضنية',
                'towns': (
                    ('minnieh', 'Minniyeh / المنية'),
                    ('bhanine', 'Bhanine / بحنين'),
                    ('deir_ammar', 'Deir Ammar / دير عمار'),
                    ('sir_el_dannieh', 'Sir El Danniyeh / سير الضنية'),
                    ('bakhoun', 'Bakhoun / بخعون'),
                ),
            },
            'zgharta': {
                'label': 'Zgharta / زغرتا',
                'towns': (
                    ('zgharta', 'Zgharta / زغرتا'),
                    ('ehden', 'Ehden / إهدن'),
                    ('rachine', 'Rachine / رشعين'),
                ),
            },
            'koura': {
                'label': 'Koura / الكورة',
                'towns': (
                    ('amioun', 'Amioun / أميون'),
                    ('anfeh', 'Anfeh / أنفه'),
                    ('kousba', 'Kousba / كوسبا'),
                    ('kfar_aaqqa', 'Kfar Aaqqa / كفرعقا'),
                ),
            },
            'bcharre': {
                'label': 'Bcharre / بشري',
                'towns': (
                    ('bcharre', 'Bcharre / بشري'),
                    ('hadath_el_jebbeh', 'Hadath El Jebbeh / حدث الجبة'),
                    ('bqaa_kafra', 'Bqaa Kafra / بقاعكفرا'),
                ),
            },
            'batroun': {
                'label': 'Batroun / البترون',
                'towns': (
                    ('batroun', 'Batroun / البترون'),
                    ('chekka', 'Chekka / شكا'),
                    ('tannourine', 'Tannourine / تنورين'),
                    ('kfar_aabida', 'Kfar Aabida / كفرعبيدا'),
                ),
            },
        },
    },
    'akkar': {
        'label': 'Akkar / عكار',
        'districts': {
            'akkar': {
                'label': 'Akkar / عكار',
                'towns': (
                    ('halba', 'Halba / حلبا'),
                    ('qoubaiyat', 'Qoubaiyat / القبيات'),
                    ('bebnine', 'Bebnine / ببنين'),
                    ('abdeh', 'Abdeh / العبدة'),
                    ('wadi_khaled', 'Wadi Khaled / وادي خالد'),
                    ('berqayel', 'Berqayel / برقايل'),
                    ('mishmish', 'Mishmish / مشمش'),
                ),
            },
        },
    },
    'bekaa': {
        'label': 'Bekaa / البقاع',
        'districts': {
            'zahle': {
                'label': 'Zahle / زحلة',
                'towns': (
                    ('zahle', 'Zahle / زحلة'),
                    ('taanayel', 'Taanayel / تعنايل'),
                    ('chtoura', 'Chtoura / شتورا'),
                    ('qabb_elias', 'Qabb Elias / قب إلياس'),
                    ('bar_elias', 'Bar Elias / بر الياس'),
                    ('majdal_anjar', 'Majdal Anjar / مجدل عنجر'),
                ),
            },
            'west_bekaa': {
                'label': 'West Bekaa / البقاع الغربي',
                'towns': (
                    ('joub_jannine', 'Joub Jannine / جب جنين'),
                    ('qaraoun', 'Qaraoun / القرعون'),
                    ('machghara', 'Machghara / مشغرة'),
                    ('sohmor', 'Sohmor / سحمر'),
                    ('gaza', 'Gaza / غزة'),
                ),
            },
            'rashaya': {
                'label': 'Rashaya / راشيا',
                'towns': (
                    ('rashaya', 'Rashaya / راشيا'),
                    ('kfar_mechki', 'Kfar Mechki / كفرمشكي'),
                    ('bakka', 'Bakka / بكا'),
                ),
            },
        },
    },
    'baalbek_hermel': {
        'label': 'Baalbek–Hermel / بعلبك–الهرمل',
        'districts': {
            'baalbek': {
                'label': 'Baalbek / بعلبك',
                'towns': (
                    ('baalbek', 'Baalbek / بعلبك'),
                    ('douris', 'Douris / دورس'),
                    ('arsal', 'Arsal / عرسال'),
                    ('labweh', 'Labweh / اللبوة'),
                    ('nabi_chit', 'Nabi Chit / النبي شيت'),
                    ('chmistar', 'Chmistar / شمسطار'),
                ),
            },
            'hermel': {
                'label': 'Hermel / الهرمل',
                'towns': (
                    ('hermel', 'Hermel / الهرمل'),
                    ('qasr', 'Qasr / القصر'),
                ),
            },
        },
    },
    'south_lebanon': {
        'label': 'South Lebanon / الجنوب',
        'districts': {
            'sidon': {
                'label': 'Sidon / صيدا',
                'towns': (
                    ('sidon', 'Sidon / صيدا'),
                    ('abra', 'Abra / عبرا'),
                    ('hlaliyeh', 'Hlaliyeh / الهلالية'),
                    ('maghdoucheh', 'Maghdoucheh / مغدوشة'),
                    ('ghazieh', 'Ghazieh / الغازية'),
                ),
            },
            'tyre': {
                'label': 'Tyre / صور',
                'towns': (
                    ('tyre', 'Tyre / صور'),
                    ('abbassiyeh', 'Abbassiyeh / العباسية'),
                    ('bourj_el_chamali', 'Bourj El Chamali / برج الشمالي'),
                    ('qana', 'Qana / قانا'),
                    ('jouaiya', 'Jouaiya / جويا'),
                    ('naqoura', 'Naqoura / الناقورة'),
                ),
            },
            'jezzine': {
                'label': 'Jezzine / جزين',
                'towns': (
                    ('jezzine', 'Jezzine / جزين'),
                    ('bkassine', 'Bkassine / بكاسين'),
                    ('lebaa', 'Lebaa / لبعا'),
                ),
            },
        },
    },
    'nabatieh': {
        'label': 'Nabatieh / النبطية',
        'districts': {
            'nabatieh': {
                'label': 'Nabatieh / النبطية',
                'towns': (
                    ('nabatieh', 'Nabatieh / النبطية'),
                    ('kfar_roummane', 'Kfar Roummane / كفررمان'),
                    ('habbouch', 'Habbouch / حبوش'),
                    ('douair', 'Douair / الدوير'),
                ),
            },
            'bint_jbeil': {
                'label': 'Bint Jbeil / بنت جبيل',
                'towns': (
                    ('bint_jbeil', 'Bint Jbeil / بنت جبيل'),
                    ('tebnine', 'Tebnine / تبنين'),
                    ('ainata', 'Ainata / عيناتا'),
                    ('aitaroun', 'Aitaroun / عيترون'),
                    ('rmeich', 'Rmeich / رميش'),
                ),
            },
            'marjayoun': {
                'label': 'Marjayoun / مرجعيون',
                'towns': (
                    ('marjayoun', 'Marjayoun / مرجعيون'),
                    ('khiam', 'Khiam / الخيام'),
                    ('kfar_kila', 'Kfar Kila / كفركلا'),
                    ('adaisseh', 'Adaisseh / العديسة'),
                    ('qlayaa', 'Qlayaa / القليعة'),
                ),
            },
            'hasbaya': {
                'label': 'Hasbaya / حاصبيا',
                'towns': (
                    ('hasbaya', 'Hasbaya / حاصبيا'),
                    ('chebaa', 'Chebaa / شبعا'),
                    ('kfar_chouba', 'Kfar Chouba / كفرشوبا'),
                    ('hebbariyeh', 'Hebbariyeh / الهبارية'),
                ),
            },
        },
    },
}

GOVERNORATE_CHOICES = tuple(
    (code, governorate['label'])
    for code, governorate in RESIDENCE_CATALOG.items()
)

DISTRICT_CHOICES = tuple(
    (code, district['label'])
    for governorate in RESIDENCE_CATALOG.values()
    for code, district in governorate['districts'].items()
)

# Flatten repeated town names once for model display choices. Parent validation
# continues to use the nested catalog: Aley is present in two source rows.
TOWN_CHOICES = tuple(dict(
    town
    for governorate in RESIDENCE_CATALOG.values()
    for district in governorate['districts'].values()
    for town in district['towns']
).items())

PROGRAMME_CHOICES = (
    (
        'BLN',
        'Basic Literacy and Numeracy (BLN) / '
        'برنامج المهارات الأساسية في القراءة والكتابة والحساب (BLN)',
    ),
    ('DIRASA', 'DIRASA / دراسة'),
)

GRADE_CHOICES = (
    ('2', 'Grade 2 / الصف الثاني'),
    ('3', 'Grade 3 / الصف الثالث'),
    ('4', 'Grade 4 / الصف الرابع'),
    ('5', 'Grade 5 / الصف الخامس'),
    ('6', 'Grade 6 / الصف السادس'),
    ('7', 'Grade 7 / الصف السابع'),
)

MATH_LANGUAGE_CHOICES = (
    ('ar', 'Arabic / العربية'),
    ('en', 'English / الإنكليزية'),
    ('fr', 'French / الفرنسية'),
)

LANGUAGE_EXAM_CHOICES = (
    ('en', 'English / الإنكليزية'),
    ('fr', 'French / الفرنسية'),
)


def district_choices(governorate):
    """Return only districts belonging to the selected governorate."""
    districts = RESIDENCE_CATALOG.get(governorate, {}).get('districts', {})
    return tuple((code, district['label']) for code, district in districts.items())


def town_choices(governorate, district):
    """Return only the supplied towns belonging to both selected parents."""
    districts = RESIDENCE_CATALOG.get(governorate, {}).get('districts', {})
    return districts.get(district, {}).get('towns', ())


def residence_labels(governorate, district, town):
    """Resolve saved codes within their parents; invalid selections stay blank."""
    governorate_data = RESIDENCE_CATALOG.get(governorate, {})
    district_data = governorate_data.get('districts', {}).get(district, {})
    town_label = dict(district_data.get('towns', ())).get(town, '')
    return (
        governorate_data.get('label', ''),
        district_data.get('label', ''),
        town_label,
    )


def valid_residence(governorate, district, town):
    """Validate the complete governorate/district/town selection hierarchy."""
    return bool(town) and town in dict(town_choices(governorate, district))
