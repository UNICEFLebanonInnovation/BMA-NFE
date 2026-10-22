"""Translated exceptional-exam choices from the supplied NFE MIS document.

Residence choices belong to this exam form, rather than the shared Location
model. Keep the document's parent relationships and Arabic spelling: a town
can appear under more than one district in the supplied table.
"""

from django.utils.translation import gettext_lazy as _, gettext_noop


def _catalog_label(label):
    """Translate the English name; retain both source names for matching."""
    return _(label.partition(' / ')[0]) if label else ''


RESIDENCE_CATALOG = {
    'beirut': {
        'label': gettext_noop('Beirut') + ' / بيروت',
        'districts': {
            'beirut': {
                'label': gettext_noop('Beirut') + ' / بيروت',
                'towns': (
                    ('achrafieh', gettext_noop('Achrafieh') + ' / الأشرفية'),
                    ('moussaitbeh', gettext_noop('Moussaitbeh') + ' / المصيطبة'),
                    ('ras_beirut', gettext_noop('Ras Beirut') + ' / رأس بيروت'),
                    ('mazraa', gettext_noop('Mazraa') + ' / المزرعة'),
                    ('medawar', gettext_noop('Medawar') + ' / المدور'),
                    ('minet_el_hosn', gettext_noop('Minet El Hosn') + ' / ميناء الحصن'),
                    ('zokak_el_blat', gettext_noop('Zokak El Blat') + ' / زقاق البلاط'),
                ),
            },
        },
    },
    'mount_lebanon': {
        'label': gettext_noop('Mount Lebanon') + ' / جبل لبنان',
        'districts': {
            'baabda': {
                'label': gettext_noop('Baabda') + ' / بعبدا',
                'towns': (
                    ('baabda', gettext_noop('Baabda') + ' / بعبدا'),
                    ('hadath', gettext_noop('Hadath') + ' / الحدث'),
                    ('hazmieh', gettext_noop('Hazmieh') + ' / الحازمية'),
                    ('chiyah', gettext_noop('Chiyah') + ' / الشياح'),
                    ('furn_el_chebbak', gettext_noop('Furn El Chebbak') + ' / فرن الشباك'),
                    ('kfarshima', gettext_noop('Kfarshima') + ' / كفرشيما'),
                    ('aley', gettext_noop('Aley') + ' / عاليه'),
                ),
            },
            'metn': {
                'label': gettext_noop('Metn') + ' / المتن',
                'towns': (
                    ('jdeideh', gettext_noop('Jdeideh') + ' / الجديدة'),
                    ('bouchrieh', gettext_noop('Bouchrieh') + ' / البوشرية'),
                    ('sed_el_bouchrieh', gettext_noop('Sed El Bouchrieh') + ' / سد البوشرية'),
                    ('bourj_hammoud', gettext_noop('Bourj Hammoud') + ' / برج حمود'),
                    ('antelias', gettext_noop('Antelias') + ' / أنطلياس'),
                    ('jal_el_dib', gettext_noop('Jal El Dib') + ' / جل الديب'),
                    ('bikfaya', gettext_noop('Bikfaya') + ' / بكفيا'),
                    ('broummana', gettext_noop('Broummana') + ' / برمانا'),
                ),
            },
            'keserwan': {
                'label': gettext_noop('Keserwan') + ' / كسروان',
                'towns': (
                    ('jounieh', gettext_noop('Jounieh') + ' / جونية'),
                    ('ghazir', gettext_noop('Ghazir') + ' / غزير'),
                    ('zouk_mikael', gettext_noop('Zouk Mikael') + ' / ذوق مكايل'),
                    ('zouk_mosbeh', gettext_noop('Zouk Mosbeh') + ' / ذوق مصبح'),
                    ('ajaltoun', gettext_noop('Ajaltoun') + ' / عجلتون'),
                    ('faraya', gettext_noop('Faraya') + ' / فاريا'),
                ),
            },
            'jbeil': {
                'label': gettext_noop('Jbeil') + ' / جبيل',
                'towns': (
                    ('jbeil', gettext_noop('Jbeil') + ' / جبيل'),
                    ('amchit', gettext_noop('Amchit') + ' / عمشيت'),
                    ('halat', gettext_noop('Halat') + ' / حالات'),
                    ('qartaba', gettext_noop('Qartaba') + ' / قرطبا'),
                    ('lassa', gettext_noop('Lassa') + ' / لاسا'),
                ),
            },
            'aley': {
                'label': gettext_noop('Aley') + ' / عاليه',
                'towns': (
                    ('aley', gettext_noop('Aley') + ' / عاليه'),
                    ('bhamdoun', gettext_noop('Bhamdoun') + ' / بحمدون'),
                    ('souq_el_gharb', gettext_noop('Souq El Gharb') + ' / سوق الغرب'),
                    ('aramoun', gettext_noop('Aramoun') + ' / عرمون'),
                    ('bchamoun', gettext_noop('Bchamoun') + ' / بشامون'),
                    ('choueifat', gettext_noop('Choueifat') + ' / شويفات'),
                ),
            },
            'chouf': {
                'label': gettext_noop('Chouf') + ' / الشوف',
                'towns': (
                    ('beit_eddine', gettext_noop('Beit Eddine') + ' / بيت الدين'),
                    ('deir_el_qamar', gettext_noop('Deir El Qamar') + ' / دير القمر'),
                    ('baakline', gettext_noop('Baakline') + ' / بعقلين'),
                    ('moukhtara', gettext_noop('Moukhtara') + ' / المختارة'),
                    ('barja', gettext_noop('Barja') + ' / برجا'),
                    ('chhim', gettext_noop('Chhim') + ' / شحيم'),
                    ('damour', gettext_noop('Damour') + ' / الدامور'),
                ),
            },
        },
    },
    'north_lebanon': {
        'label': gettext_noop('North Lebanon') + ' / الشمال',
        'districts': {
            'tripoli': {
                'label': gettext_noop('Tripoli') + ' / طرابلس',
                'towns': (
                    ('tripoli', gettext_noop('Tripoli') + ' / طرابلس'),
                    ('el_mina', gettext_noop('El Mina') + ' / الميناء'),
                    ('qobbeh', gettext_noop('Qobbeh') + ' / القبة'),
                    ('abi_samra', gettext_noop('Abi Samra') + ' / أبي سمراء'),
                    ('tebbaneh', gettext_noop('Tebbaneh') + ' / التبانة'),
                ),
            },
            'minnieh_dannieh': {
                'label': gettext_noop('Minniyeh–Danniyeh') + ' / المنية–الضنية',
                'towns': (
                    ('minnieh', gettext_noop('Minniyeh') + ' / المنية'),
                    ('bhanine', gettext_noop('Bhanine') + ' / بحنين'),
                    ('deir_ammar', gettext_noop('Deir Ammar') + ' / دير عمار'),
                    ('sir_el_dannieh', gettext_noop('Sir El Danniyeh') + ' / سير الضنية'),
                    ('bakhoun', gettext_noop('Bakhoun') + ' / بخعون'),
                ),
            },
            'zgharta': {
                'label': gettext_noop('Zgharta') + ' / زغرتا',
                'towns': (
                    ('zgharta', gettext_noop('Zgharta') + ' / زغرتا'),
                    ('ehden', gettext_noop('Ehden') + ' / إهدن'),
                    ('rachine', gettext_noop('Rachine') + ' / رشعين'),
                ),
            },
            'koura': {
                'label': gettext_noop('Koura') + ' / الكورة',
                'towns': (
                    ('amioun', gettext_noop('Amioun') + ' / أميون'),
                    ('anfeh', gettext_noop('Anfeh') + ' / أنفه'),
                    ('kousba', gettext_noop('Kousba') + ' / كوسبا'),
                    ('kfar_aaqqa', gettext_noop('Kfar Aaqqa') + ' / كفرعقا'),
                ),
            },
            'bcharre': {
                'label': gettext_noop('Bcharre') + ' / بشري',
                'towns': (
                    ('bcharre', gettext_noop('Bcharre') + ' / بشري'),
                    ('hadath_el_jebbeh', gettext_noop('Hadath El Jebbeh') + ' / حدث الجبة'),
                    ('bqaa_kafra', gettext_noop('Bqaa Kafra') + ' / بقاعكفرا'),
                ),
            },
            'batroun': {
                'label': gettext_noop('Batroun') + ' / البترون',
                'towns': (
                    ('batroun', gettext_noop('Batroun') + ' / البترون'),
                    ('chekka', gettext_noop('Chekka') + ' / شكا'),
                    ('tannourine', gettext_noop('Tannourine') + ' / تنورين'),
                    ('kfar_aabida', gettext_noop('Kfar Aabida') + ' / كفرعبيدا'),
                ),
            },
        },
    },
    'akkar': {
        'label': gettext_noop('Akkar') + ' / عكار',
        'districts': {
            'akkar': {
                'label': gettext_noop('Akkar') + ' / عكار',
                'towns': (
                    ('halba', gettext_noop('Halba') + ' / حلبا'),
                    ('qoubaiyat', gettext_noop('Qoubaiyat') + ' / القبيات'),
                    ('bebnine', gettext_noop('Bebnine') + ' / ببنين'),
                    ('abdeh', gettext_noop('Abdeh') + ' / العبدة'),
                    ('wadi_khaled', gettext_noop('Wadi Khaled') + ' / وادي خالد'),
                    ('berqayel', gettext_noop('Berqayel') + ' / برقايل'),
                    ('mishmish', gettext_noop('Mishmish') + ' / مشمش'),
                ),
            },
        },
    },
    'bekaa': {
        'label': gettext_noop('Bekaa') + ' / البقاع',
        'districts': {
            'zahle': {
                'label': gettext_noop('Zahle') + ' / زحلة',
                'towns': (
                    ('zahle', gettext_noop('Zahle') + ' / زحلة'),
                    ('taanayel', gettext_noop('Taanayel') + ' / تعنايل'),
                    ('chtoura', gettext_noop('Chtoura') + ' / شتورا'),
                    ('qabb_elias', gettext_noop('Qabb Elias') + ' / قب إلياس'),
                    ('bar_elias', gettext_noop('Bar Elias') + ' / بر الياس'),
                    ('majdal_anjar', gettext_noop('Majdal Anjar') + ' / مجدل عنجر'),
                ),
            },
            'west_bekaa': {
                'label': gettext_noop('West Bekaa') + ' / البقاع الغربي',
                'towns': (
                    ('joub_jannine', gettext_noop('Joub Jannine') + ' / جب جنين'),
                    ('qaraoun', gettext_noop('Qaraoun') + ' / القرعون'),
                    ('machghara', gettext_noop('Machghara') + ' / مشغرة'),
                    ('sohmor', gettext_noop('Sohmor') + ' / سحمر'),
                    ('gaza', gettext_noop('Gaza') + ' / غزة'),
                ),
            },
            'rashaya': {
                'label': gettext_noop('Rashaya') + ' / راشيا',
                'towns': (
                    ('rashaya', gettext_noop('Rashaya') + ' / راشيا'),
                    ('kfar_mechki', gettext_noop('Kfar Mechki') + ' / كفرمشكي'),
                    ('bakka', gettext_noop('Bakka') + ' / بكا'),
                ),
            },
        },
    },
    'baalbek_hermel': {
        'label': gettext_noop('Baalbek–Hermel') + ' / بعلبك–الهرمل',
        'districts': {
            'baalbek': {
                'label': gettext_noop('Baalbek') + ' / بعلبك',
                'towns': (
                    ('baalbek', gettext_noop('Baalbek') + ' / بعلبك'),
                    ('douris', gettext_noop('Douris') + ' / دورس'),
                    ('arsal', gettext_noop('Arsal') + ' / عرسال'),
                    ('labweh', gettext_noop('Labweh') + ' / اللبوة'),
                    ('nabi_chit', gettext_noop('Nabi Chit') + ' / النبي شيت'),
                    ('chmistar', gettext_noop('Chmistar') + ' / شمسطار'),
                ),
            },
            'hermel': {
                'label': gettext_noop('Hermel') + ' / الهرمل',
                'towns': (
                    ('hermel', gettext_noop('Hermel') + ' / الهرمل'),
                    ('qasr', gettext_noop('Qasr') + ' / القصر'),
                ),
            },
        },
    },
    'south_lebanon': {
        'label': gettext_noop('South Lebanon') + ' / الجنوب',
        'districts': {
            'sidon': {
                'label': gettext_noop('Sidon') + ' / صيدا',
                'towns': (
                    ('sidon', gettext_noop('Sidon') + ' / صيدا'),
                    ('abra', gettext_noop('Abra') + ' / عبرا'),
                    ('hlaliyeh', gettext_noop('Hlaliyeh') + ' / الهلالية'),
                    ('maghdoucheh', gettext_noop('Maghdoucheh') + ' / مغدوشة'),
                    ('ghazieh', gettext_noop('Ghazieh') + ' / الغازية'),
                ),
            },
            'tyre': {
                'label': gettext_noop('Tyre') + ' / صور',
                'towns': (
                    ('tyre', gettext_noop('Tyre') + ' / صور'),
                    ('abbassiyeh', gettext_noop('Abbassiyeh') + ' / العباسية'),
                    ('bourj_el_chamali', gettext_noop('Bourj El Chamali') + ' / برج الشمالي'),
                    ('qana', gettext_noop('Qana') + ' / قانا'),
                    ('jouaiya', gettext_noop('Jouaiya') + ' / جويا'),
                    ('naqoura', gettext_noop('Naqoura') + ' / الناقورة'),
                ),
            },
            'jezzine': {
                'label': gettext_noop('Jezzine') + ' / جزين',
                'towns': (
                    ('jezzine', gettext_noop('Jezzine') + ' / جزين'),
                    ('bkassine', gettext_noop('Bkassine') + ' / بكاسين'),
                    ('lebaa', gettext_noop('Lebaa') + ' / لبعا'),
                ),
            },
        },
    },
    'nabatieh': {
        'label': gettext_noop('Nabatieh') + ' / النبطية',
        'districts': {
            'nabatieh': {
                'label': gettext_noop('Nabatieh') + ' / النبطية',
                'towns': (
                    ('nabatieh', gettext_noop('Nabatieh') + ' / النبطية'),
                    ('kfar_roummane', gettext_noop('Kfar Roummane') + ' / كفررمان'),
                    ('habbouch', gettext_noop('Habbouch') + ' / حبوش'),
                    ('douair', gettext_noop('Douair') + ' / الدوير'),
                ),
            },
            'bint_jbeil': {
                'label': gettext_noop('Bint Jbeil') + ' / بنت جبيل',
                'towns': (
                    ('bint_jbeil', gettext_noop('Bint Jbeil') + ' / بنت جبيل'),
                    ('tebnine', gettext_noop('Tebnine') + ' / تبنين'),
                    ('ainata', gettext_noop('Ainata') + ' / عيناتا'),
                    ('aitaroun', gettext_noop('Aitaroun') + ' / عيترون'),
                    ('rmeich', gettext_noop('Rmeich') + ' / رميش'),
                ),
            },
            'marjayoun': {
                'label': gettext_noop('Marjayoun') + ' / مرجعيون',
                'towns': (
                    ('marjayoun', gettext_noop('Marjayoun') + ' / مرجعيون'),
                    ('khiam', gettext_noop('Khiam') + ' / الخيام'),
                    ('kfar_kila', gettext_noop('Kfar Kila') + ' / كفركلا'),
                    ('adaisseh', gettext_noop('Adaisseh') + ' / العديسة'),
                    ('qlayaa', gettext_noop('Qlayaa') + ' / القليعة'),
                ),
            },
            'hasbaya': {
                'label': gettext_noop('Hasbaya') + ' / حاصبيا',
                'towns': (
                    ('hasbaya', gettext_noop('Hasbaya') + ' / حاصبيا'),
                    ('chebaa', gettext_noop('Chebaa') + ' / شبعا'),
                    ('kfar_chouba', gettext_noop('Kfar Chouba') + ' / كفرشوبا'),
                    ('hebbariyeh', gettext_noop('Hebbariyeh') + ' / الهبارية'),
                ),
            },
        },
    },
}

GOVERNORATE_CHOICES = tuple(
    (code, _catalog_label(governorate['label']))
    for code, governorate in RESIDENCE_CATALOG.items()
)

DISTRICT_CHOICES = tuple(
    (code, _catalog_label(district['label']))
    for governorate in RESIDENCE_CATALOG.values()
    for code, district in governorate['districts'].items()
)

# Flatten repeated town names once for model display choices. Parent validation
# continues to use the nested catalog: Aley is present in two source rows.
TOWN_CHOICES = tuple(dict(
    (code, _catalog_label(label))
    for governorate in RESIDENCE_CATALOG.values()
    for district in governorate['districts'].values()
    for code, label in district['towns']
).items())

PROGRAMME_CHOICES = (
    ('BLN Level 1', _('BLN Level 1')),
    ('BLN Level 2', _('BLN Level 2')),
    ('BLN Level 3', _('BLN Level 3')),
)

COUNTRY_OF_BIRTH_CHOICES = (
    ('LB', _('Lebanon')),
    ('SY', _('Syria')),
    ('OTHER', _('Other')),
)

GRADE_CHOICES = (
    ('2', _('Grade 2')),
    ('3', _('Grade 3')),
    ('4', _('Grade 4')),
)

MATH_LANGUAGE_CHOICES = (
    ('ar', _('Arabic')),
    ('en', _('English')),
    ('fr', _('French')),
)

LANGUAGE_EXAM_CHOICES = (
    ('en', _('English')),
    ('fr', _('French')),
)


def district_choices(governorate):
    """Return only districts belonging to the selected governorate."""
    districts = RESIDENCE_CATALOG.get(governorate, {}).get('districts', {})
    return tuple((code, _catalog_label(district['label'])) for code, district in districts.items())


def town_choices(governorate, district):
    """Return only the supplied towns belonging to both selected parents."""
    districts = RESIDENCE_CATALOG.get(governorate, {}).get('districts', {})
    return tuple(
        (code, _catalog_label(label))
        for code, label in districts.get(district, {}).get('towns', ())
    )


def residence_labels(governorate, district, town):
    """Resolve saved codes within their parents; invalid selections stay blank."""
    governorate_data = RESIDENCE_CATALOG.get(governorate, {})
    district_data = governorate_data.get('districts', {}).get(district, {})
    town_label = dict(district_data.get('towns', ())).get(town, '')
    return (
        _catalog_label(governorate_data.get('label', '')),
        _catalog_label(district_data.get('label', '')),
        _catalog_label(town_label),
    )


def valid_residence(governorate, district, town):
    """Validate the complete governorate/district/town selection hierarchy."""
    return bool(town) and town in dict(town_choices(governorate, district))
