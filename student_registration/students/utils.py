import io
import xlwt
import csv
import copy
from datetime import date
from django.http import HttpResponse, FileResponse
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, Color
from datetime import datetime
import logging
from django.conf import settings
import requests
from requests.structures import CaseInsensitiveDict
import json
logger = logging.getLogger(__name__)


def get_api_token():

    try:
        body = {
            "username": settings.UNIQUE_ID_API_USERNAME,
            "password": settings.UNIQUE_ID_API_PASSWORD
        }

        resp = requests.post(settings.UNIQUE_ID_API_TOKEN_URL, data=body)
        result = json.loads(resp.text)

        return result['token'] if "token" in result else 0
    except Exception as ex:
        return 0


def get_api_data(token, data):

    try:

        headers = CaseInsensitiveDict()
        headers["Authorization"] = token
        json_data = json.dumps(data)
        resp = requests.post(settings.UNIQUE_ID_API_URL, headers=headers, data=json_data)
        result = json.loads(resp.text)

        individuals = result["individual"] if "individual" in result else []
        if len(individuals) == 1:
            return individuals[0]
        return individuals
    except Exception as ex:
        return 0


def generate_one_unique_id(pk,first_name,father_name, last_name, mother_fullname, birthdate, nationality, sex):
    try:
        token = get_api_token()
        if not token:
            return 0
        data = {
            "individuals": [
                {
                    "id": pk,
                    "first_name": first_name,
                    "father_name": father_name,
                    "last_name": last_name,
                    "mother_name": mother_fullname,
                    "date_of_birth": birthdate,
                    "nationality": nationality,
                    "gender": sex
                }
            ]
        }
        result = get_api_data(token, data)
        return result["unicef_id"]
    except Exception as ex:
        return 0


def generate_bulk_unique_id(data):
    token = get_api_token()
    if not token:
        return 0

    data = get_api_data(token, data)
    return {int(indiv["id"]): indiv["unicef_id"] for indiv in data}


def get_api_programmes(token, data):

    try:

        headers = CaseInsensitiveDict()
        headers["Authorization"] = token
        json_data = json.dumps(data)

        resp = requests.post(settings.UNIQUE_PROGRAMMES_API_URL, headers=headers, data=json_data)
        logger.info(resp)
        logger.info(resp.text)
        result = json.loads(resp.text)

        individuals = result["individuals"] if "individuals" in result else []
        if len(individuals) == 1:
            return individuals[0]
        return individuals
    except Exception as ex:
        logger.exception(ex)
        return 0


def get_bulk_programmes(data):
    token = get_api_token()
    if not token:
        return 0

    data = get_api_programmes(token, data)

    result = {
        int(indiv["unique_id"]): indiv["programmes"]
        for indiv in data
        if "programmes" in indiv
    }
    return result


def generate_id(
            first_name,
            father_name,
            last_name,
            mother_full_name,
            gender,
            birthday_day,
            birthday_month,
            birthday_year
        ):
    """
    Unique Number Proposal:
    full name total char number
    mother full name total char number
    Concatenate hash number for: first name, father name and last name
    Concatenate hash number for: mother first name and mother last name
    Concatenate hash number for birthday: day, month, year
    Gender type first letter

    :return:
    """
    import hashlib

    try:
        # concatenate name to form full name with no spaces
        full_name = u'{}{}{}'.format(first_name, father_name, last_name)

        # take the count of full name and zero pad to two digits
        full_name_char_count = '{0:0>2}'.format(len(full_name))

        # take the count of mother name and zero pad to two digits
        mother_name_char_count = '{0:0>2}'.format(len(mother_full_name))

        # take the hash of fullname and convert to integer, zero padding to 4 digits
        full_name_hash = '{0:0>4}'.format(int(hashlib.sha1(full_name.encode('UTF-8')).hexdigest(), 16) % 10000)

        # take the hash of mother name and convert to integer, zero padding to 4 digits
        mother_name_hash = '{0:0>3}'.format(int(hashlib.sha1(mother_full_name.encode('UTF-8')).hexdigest(), 16) % 1000)

        # take the first character of the gender to denote sex
        gender_first_char = gender[:1]

        # concatenate day, month and year to form birthday without space or special characters
        birthday = u'{}{}{}'.format(birthday_day, birthday_month, birthday_year)

        # take the hash of birthday and convert to integer, zero padding to 3 digits
        birthday_hash = '{0:0>3}'.format(int(hashlib.sha1(birthday.encode()).hexdigest(), 16) % 1000)

        # arrange in order
        result = '{fullname_char}{mothername_char}{fullname_hash}{mothername_hash}{birthday}{gender_char}'.format(
            fullname_char=full_name_char_count,
            mothername_char=mother_name_char_count,
            fullname_hash=full_name_hash,
            mothername_hash=mother_name_hash,
            birthday=birthday_hash,
            gender_char=gender_first_char
        )
        return result

    except Exception as exp:
        return ''


def is_allowed_create(programme):
    from student_registration.schools.models import CLMRound
    try:
        current = date.today()
        current_round = CLMRound.objects.all()

        if programme == 'Bridging':
            current_round = current_round.get(current_round_bridging=True)
            if current_round.start_date_bridging < current < current_round.end_date_bridging:
                return True
            return False

    except Exception as ex:
        return False


def is_allowed_edit(programme):
    from student_registration.schools.models import CLMRound

    try:
        current = date.today()
        current_round = CLMRound.objects.all()

        if programme == 'Bridging':
            current_round = current_round.get(current_round_bridging=True)
            if current_round.start_date_bridging_edit < current < current_round.end_date_bridging_edit:
                return True
            return False

    except Exception as ex:
        return False


def listToString(s):
    # initialize an empty string
    str1 = ""

    # traverse in the string
    for ele in s:
        if str1 == "":
            str1 += ele
        else:
            str1 += "," + ele

        # return string
    return str1


class MemorySavingQuerysetIterator(object):

    def __init__(self, queryset, max_obj_num=1000):
        self._base_queryset = queryset
        self._generator = self._setup()
        self.max_obj_num = max_obj_num

    def _setup(self):
        for i in xrange(0, self._base_queryset.count(), self.max_obj_num):
            # By making a copy of the queryset and using that to actually access
            # the objects we ensure that there are only `max_obj_num` objects in
            # memory at any given time
            smaller_queryset = copy.deepcopy(self._base_queryset)[i:i + self.max_obj_num]
            # logger.debug('Grabbing next %s objects from DB' % self.max_obj_num)
            for obj in smaller_queryset.iterator():
                yield obj

    def __iter__(self):
        return self

    def next(self):
        return self._generator.next()
