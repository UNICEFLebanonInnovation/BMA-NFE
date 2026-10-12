"""Connect exam residence choices to the existing Location hierarchy."""

import re
import unicodedata

from .exceptional_exam_choices import RESIDENCE_CATALOG, town_choices


def location_label(location):
    """Display both stored languages without repeating identical names."""
    if not location:
        return ''
    names = []
    for value in (location.name_en, location.name):
        value = str(value).strip() if value else ''
        if value and value not in names:
            names.append(value)
    return ' / '.join(names)


def normalized_name(value):
    """Ignore presentation punctuation without guessing similar place names."""
    value = unicodedata.normalize('NFKC', str(value or '')).casefold()
    return re.sub(r'[\W_]+', ' ', value, flags=re.UNICODE).strip()


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


def _matching_code(location, labelled_codes, aliases=None):
    names = {
        normalized_name(value)
        for value in (location.name, location.name_en) if value
    }
    matches = []
    for code, label in labelled_codes:
        labels = label.split(' / ') + list((aliases or {}).get(code, ()))
        if names.intersection(normalized_name(value) for value in labels):
            matches.append(code)
    return matches[0] if len(matches) == 1 else ''


def catalog_governorate_code(governorate):
    """Resolve the document's governorate only from its exact stored names."""
    if not governorate or governorate.type_id != 1:
        return ''
    return _matching_code(
        governorate,
        ((code, data['label']) for code, data in RESIDENCE_CATALOG.items()),
        GOVERNORATE_ALIASES,
    )


def catalog_location_codes(governorate, district):
    """Resolve a district inside its actual parent before showing town choices."""
    governorate_code = catalog_governorate_code(governorate)
    if not (governorate and governorate.type_id == 1 and district and district.type_id == 2
            and district.parent_id == governorate.pk):
        return governorate_code, ''
    if governorate_code:
        districts = RESIDENCE_CATALOG[governorate_code]['districts']
        district_code = _matching_code(
            district, ((code, data['label']) for code, data in districts.items()),
        )
        if district_code:
            return governorate_code, district_code

    # The deployed Location hierarchy can predate the document's governorate
    # boundaries (for example Bekaa -> Baalbek). Its parent IDs remain the
    # authority; an exact, unique district name identifies the village list.
    names = {
        normalized_name(value) for value in (district.name, district.name_en) if value
    }
    matches = [
        (code, district_code)
        for code, governorate_data in RESIDENCE_CATALOG.items()
        for district_code, district_data in governorate_data['districts'].items()
        if names.intersection(
            normalized_name(value) for value in district_data['label'].split(' / ')
        )
    ]
    return matches[0] if len(matches) == 1 else (governorate_code, '')


def town_choices_for_locations(governorate, district):
    """Use the attached village list for the selected Location district."""
    return town_choices(*catalog_location_codes(governorate, district))


def positive_location_id(value):
    try:
        location_id = int(getattr(value, 'pk', value))
    except (TypeError, ValueError):
        return None
    return location_id if location_id > 0 else None
