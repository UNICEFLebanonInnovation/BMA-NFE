"""Tests for the Dirasa (Bridging) child profile ID card and bulk PDF generation."""

import datetime
import re

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.files.uploadedfile import SimpleUploadedFile
from django.http import HttpResponse

from student_registration.backends import profile_ids
from student_registration.backends.models import ExportHistory
from student_registration.backends.profile_ids import shape_text
from student_registration.clm import profile_id as clm_profile_id
from student_registration.clm.bridging_views import bridging_profile_id_card
from student_registration.clm.models import Bridging, Disability
from student_registration.clm.profile_id import build_profile_ids_pdf
from student_registration.locations.models import Location, LocationType
from student_registration.schools.models import CLMRound, PartnerOrganization
from student_registration.students.models import Nationality, Student

pytestmark = pytest.mark.django_db

# Smallest valid 1x1 GIF, enough for ImageField validation.
GIF = (b'GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff!\xf9\x04\x01\x00\x00\x00\x00,'
       b'\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;')


def _page_count(pdf_bytes):
    assert pdf_bytes.startswith(b'%PDF')
    return len(re.findall(rb'/Type\s*/Page\b(?!s)', pdf_bytes))


@pytest.fixture
def registration():
    governorate = LocationType.objects.create(name='Governorate')
    baalbek = Location.objects.create(name='بعلبك الهرمل', name_en='Baalbek-Hermel', p_code='LB2', type=governorate)
    student = Student.objects.create(
        first_name='ريهام', father_name='علي', last_name='الشمق',
        birthday_day='5', birthday_month='5', birthday_year='2014',
        place_of_birth='Hazmieh',
        nationality=Nationality.objects.create(name='سوري', name_en='Syrian'),
    )
    return Bridging.objects.create(
        student=student,
        round=CLMRound.objects.create(name='2026-2027', current_year=True, current_round_bridging=True,
                                      start_date_bridging=datetime.date.today() - datetime.timedelta(days=30),
                                      end_date_bridging=datetime.date.today() + datetime.timedelta(days=30),
                                      start_date_bridging_edit=datetime.date.today() - datetime.timedelta(days=30),
                                      end_date_bridging_edit=datetime.date.today() + datetime.timedelta(days=30)),
        partner=PartnerOrganization.objects.create(name='SAVE'),
        governorate=baalbek,
        disability=Disability.objects.create(name='لا', name_en='No'),
    )


@pytest.fixture
def classmates(registration):
    """A second child of the same partner and one child of another partner."""
    second = Bridging.objects.create(
        student=Student.objects.create(first_name='أحمد', father_name='خالد', last_name='حسن',
                                       birthday_day='1', birthday_month='2', birthday_year='2013',
                                       nationality=registration.student.nationality),
        round=registration.round, partner=registration.partner, governorate=registration.governorate,
    )
    other = Bridging.objects.create(
        student=Student.objects.create(first_name='Other', father_name='Partner', last_name='Child'),
        round=registration.round, partner=PartnerOrganization.objects.create(name='OTHER'),
        governorate=registration.governorate,
    )
    return {'second': second, 'other': other}


@pytest.fixture
def bridging_client(client):
    user = get_user_model().objects.create_user(username='dirasa', password='x-pass-123456')
    user.groups.add(Group.objects.get_or_create(name='CLM_Bridging')[0])
    client.force_login(user)
    return client


@pytest.fixture
def partner_client(client, registration):
    user = get_user_model().objects.create_user(username='save', password='x-pass-123456',
                                                partner=registration.partner)
    user.groups.add(Group.objects.get_or_create(name='CLM_Bridging')[0])
    client.force_login(user)
    return client


@pytest.fixture
def local_media(settings, tmp_path):
    settings.MEDIA_ROOT = str(tmp_path)
    settings.STORAGES = {
        'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
        'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'},
    }


class FakeExportStorage(object):
    saved = {}

    def save(self, name, content):
        FakeExportStorage.saved[name] = content.read()
        return name


@pytest.fixture
def fake_storage(monkeypatch):
    FakeExportStorage.saved = {}
    monkeypatch.setattr(profile_ids, 'ExportStorage', FakeExportStorage)
    return FakeExportStorage


@pytest.fixture
def pushes(monkeypatch):
    sent = []
    monkeypatch.setattr(profile_ids, 'send_push_to_web', lambda user, title, body, data=None: sent.append(
        {'user': user, 'title': title, 'body': body, 'data': data}) or True)
    return sent


@pytest.fixture
def queued(monkeypatch):
    calls = []
    monkeypatch.setattr(profile_ids, 'queue_profile_ids',
                        lambda export_id, programme, ids: calls.append((export_id, list(ids))))
    return calls


def test_card_data_matches_registration(registration):
    card = bridging_profile_id_card(registration)
    assert card == {
        'round': '2026-2027',
        'id': registration.id,
        'ngo': 'SAVE',
        'full_name': 'ريهام علي الشمق',
        'birthday': '5/5/14',
        'place_of_birth': 'Hazmieh',
        'nationality': 'Syrian',
        'governorate': 'Baalbek-Hermel',
        'physical_difficulties': 'No',
        'has_picture': False,
    }


def test_card_data_tolerates_missing_details():
    student = Student.objects.create(first_name='Only')
    bridging = Bridging.objects.create(student=student)
    card = bridging_profile_id_card(bridging)
    assert card['full_name'] == 'Only'
    assert card['birthday'] == ''
    assert card['nationality'] == ''
    assert card['governorate'] == ''
    assert card['ngo'] == ''
    assert card['round'] == ''
    assert card['physical_difficulties'] == 'No'
    assert bridging_profile_id_card(Bridging.objects.create())['full_name'] == ''


def test_shape_text_keeps_latin_and_reorders_arabic():
    assert shape_text('Nationality: Syrian') == 'Nationality: Syrian'
    shaped = shape_text('الاسم الثلاثي: ريهام')
    assert shaped != 'الاسم الثلاثي: ريهام'
    assert len(shaped) > 0


def test_profile_id_page_renders_card(bridging_client, registration):
    response = bridging_client.get('/clm/bridging-profile-id/{}/'.format(registration.id))
    assert response.status_code == 200
    html = response.content.decode('utf-8')
    for text in ('2026-2027', 'ID: {}'.format(registration.id), 'NGO: SAVE', 'ريهام علي الشمق',
                 'Date of Birth: 5/5/14', 'Place of Birth: Hazmieh', 'Nationality: Syrian',
                 'Governorate: Baalbek-Hermel', 'Physical difficulties: No',
                 'الامتحان الاستثنائي لطلاب التعليم الغير نظامي'):
        assert text in html
    assert '/clm/bridging-profile-picture/{}/image/'.format(registration.id) not in html


def test_profile_picture_upload_and_card_photo(bridging_client, registration, local_media):
    url = '/clm/bridging-profile-picture/{}/'.format(registration.id)
    response = bridging_client.get(url)
    assert response.status_code == 200
    html = response.content.decode('utf-8')
    assert 'No profile picture has been uploaded.' in html
    assert '/clm/bridging-profile-id/{}/'.format(registration.id) in html

    upload = SimpleUploadedFile('child.gif', GIF, content_type='image/gif')
    response = bridging_client.post(url, {'profile_picture': upload})
    assert response.status_code == 302
    registration.refresh_from_db()
    assert registration.profile_picture.name.startswith('uploads/bridging/profile_pictures/')

    photo_url = '/clm/bridging-profile-picture/{}/image/'.format(registration.id)
    html = bridging_client.get('/clm/bridging-profile-id/{}/'.format(registration.id)).content.decode('utf-8')
    assert photo_url in html
    image = bridging_client.get(photo_url)
    assert image.status_code == 200
    assert image['Content-Type'] == 'image/gif'


def test_pdf_has_one_page_per_child(registration, classmates, local_media):
    registration.profile_picture.save('child.gif', SimpleUploadedFile('child.gif', GIF, content_type='image/gif'))
    registrations = clm_profile_id.profile_ids_registrations([registration.id, classmates['second'].id])
    assert _page_count(build_profile_ids_pdf(registrations)) == 2
    assert _page_count(build_profile_ids_pdf([])) == 1


def test_generate_profile_ids_stores_pdf_and_notifies(registration, classmates, fake_storage, pushes):
    owner = get_user_model().objects.create_user(username='owner')
    export = ExportHistory.objects.create(export_type=clm_profile_id.PROFILE_IDS_EXPORT_TYPE, created_by=owner)
    file_url = profile_ids.generate_profile_ids(export.id, clm_profile_id.BRIDGING_PROFILE_IDS,
                                                [registration.id, classmates['second'].id])

    export.refresh_from_db()
    assert export.status == 'done'
    assert export.file_url == file_url
    assert re.match(r'^/clm/bridging-profile-ids/download/profile_ids_[0-9a-f-]+[.]pdf/$', file_url)
    assert _page_count(fake_storage.saved[file_url.split('/')[-2]]) == 2
    assert pushes == [{
        'user': owner,
        'title': 'Dirasa profile IDs ready',
        'body': 'The PDF with 2 profile ID card(s) is ready to download.',
        'data': {'type': 'profile_ids_ready', 'label': 'Dirasa', 'url': file_url, 'export_id': export.id},
    }]


def test_generate_profile_ids_failure_marks_export_failed(registration, fake_storage, pushes, monkeypatch):
    def boom(cards, title=''):
        raise RuntimeError('font missing')
    monkeypatch.setattr(profile_ids, 'build_cards_pdf', boom)
    user = get_user_model().objects.create_user(username='owner2')
    export = ExportHistory.objects.create(export_type=clm_profile_id.PROFILE_IDS_EXPORT_TYPE, created_by=user)

    assert profile_ids.generate_profile_ids(export.id, clm_profile_id.BRIDGING_PROFILE_IDS, [registration.id]) is None
    export.refresh_from_db()
    assert export.status == 'failed'
    assert export.file_url is None
    assert pushes[0]['title'] == 'Dirasa profile IDs failed'
    assert pushes[0]['data'] == {'type': 'profile_ids_failed', 'label': 'Dirasa', 'reason': 'font missing',
                                 'export_id': export.id}
    assert profile_ids.generate_profile_ids(999999, clm_profile_id.BRIDGING_PROFILE_IDS, [registration.id]) is None


def test_bulk_profile_ids_queues_visible_children(partner_client, registration, classmates, queued):
    response = partner_client.post('/clm/bridging-profile-ids/')
    assert response.status_code == 200
    export = ExportHistory.objects.get()
    assert response.json() == {'status': 'started', 'export_id': export.id, 'count': 2}
    assert export.export_type == 'Bridging Profile IDs'
    assert export.status == 'pending'
    assert export.file_format == 'pdf'
    assert export.created_by.username == 'save'
    assert export.partner_name == 'SAVE'
    assert export.fields == {'count': 2, 'filters': {}}
    assert len(queued) == 1
    assert queued[0][0] == export.id
    assert sorted(queued[0][1]) == sorted([registration.id, classmates['second'].id])


def test_bulk_profile_ids_follow_list_filters(partner_client, registration, classmates, queued):
    response = partner_client.post('/clm/bridging-profile-ids/?student__first_name=أحمد')
    assert response.json()['count'] == 1
    assert queued[-1][1] == [classmates['second'].id]

    response = partner_client.post('/clm/bridging-profile-ids/?ids={},999999'.format(registration.id))
    assert response.json()['count'] == 1
    assert queued[-1][1] == [registration.id]

    response = partner_client.post('/clm/bridging-profile-ids/?student__first_name=nobody')
    assert response.status_code == 400
    assert 'nothing to generate' in response.json()['error']
    assert partner_client.get('/clm/bridging-profile-ids/').status_code == 405


def test_bulk_profile_ids_all_group_sees_every_partner(bridging_client, registration, classmates, queued):
    user = get_user_model().objects.get(username='dirasa')
    user.groups.add(Group.objects.get_or_create(name='CLM_BRIDGING_ALL')[0])
    assert bridging_client.post('/clm/bridging-profile-ids/').json()['count'] == 3


def test_profile_ids_download(bridging_client, monkeypatch):
    calls = []
    monkeypatch.setattr(profile_ids, 'download_file',
                        lambda name, returned, content_type=None: calls.append((name, returned, content_type))
                        or HttpResponse(b'%PDF', content_type=content_type))
    name = 'profile_ids_0f1e2d3c-4b5a-6978-8a9b-0c1d2e3f4a5b.pdf'
    response = bridging_client.get('/clm/bridging-profile-ids/download/{}/'.format(name))
    assert response.status_code == 200
    assert calls == [(name, 'profile_ids.pdf', 'application/pdf')]
    assert bridging_client.get('/clm/bridging-profile-ids/download/..%2Fsecret.pdf/').status_code == 400
    assert bridging_client.get('/clm/bridging-profile-ids/download/export.csv/').status_code == 400


def test_profile_ids_pages_require_login(client, registration):
    for url in ('/clm/bridging-profile-id/{}/'.format(registration.id),
                '/clm/bridging-profile-picture/{}/'.format(registration.id),
                '/clm/bridging-profile-ids/download/profile_ids_0f1e2d3c-4b5a-6978-8a9b-0c1d2e3f4a5b.pdf/'):
        assert client.get(url).status_code == 302
    assert client.post('/clm/bridging-profile-ids/').status_code == 302


def test_list_page_links_to_bulk_profile_ids(partner_client, registration):
    response = partner_client.get('/clm/bridging-list/')
    assert response.status_code == 200
    html = response.content.decode('utf-8')
    assert 'data-url="/clm/bridging-profile-ids/"' in html
    assert 'Generate Profile IDs (PDF)' in html
    assert '/clm/bridging-profile-picture/{}'.format(registration.id) in html
    assert '/clm/bridging-profile-id/{}'.format(registration.id) in html
