"""Tests for the Makani (MSCC) child profile ID card and bulk PDF generation."""

import re

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.files.uploadedfile import SimpleUploadedFile

from student_registration.backends import profile_ids
from student_registration.backends.models import ExportHistory
from student_registration.child.models import Child
from student_registration.clm.models import Disability
from student_registration.locations.models import Center, Location, LocationType
from student_registration.mscc import models as m
from student_registration.mscc.profile_id import MAKANI_PROFILE_IDS, build_profile_ids_pdf, registration_profile_id_card
from student_registration.schools.models import PartnerOrganization
from student_registration.students.models import IDType, Nationality

pytestmark = pytest.mark.django_db

GIF = (b'GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff!\xf9\x04\x01\x00\x00\x00\x00,'
       b'\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;')


def _page_count(pdf_bytes):
    assert pdf_bytes.startswith(b'%PDF')
    return len(re.findall(rb'/Type\s*/Page\b(?!s)', pdf_bytes))


@pytest.fixture
def makani():
    governorate = LocationType.objects.create(name='Governorate')
    baalbek = Location.objects.create(name='بعلبك الهرمل', name_en='Baalbek-Hermel', p_code='LB2', type=governorate)
    partner = PartnerOrganization.objects.create(name='SAVE')
    other_partner = PartnerOrganization.objects.create(name='OTHER')
    center = Center.objects.create(name='Center A', partner=partner, governorate=baalbek)
    other_center = Center.objects.create(name='Center B', partner=other_partner, governorate=baalbek)
    current = m.Round.objects.create(name='2026-2027', current_year=True)
    syrian = Nationality.objects.create(name='سوري', name_en='Syrian')
    no = Disability.objects.create(name='لا', name_en='No')

    child = Child.objects.create(first_name='ريهام', father_name='علي', last_name='الشمق', gender='Female',
                                 birthday_day='5', birthday_month='5', birthday_year='2014',
                                 nationality=syrian, disability=no,
                                 id_type=IDType.objects.create(name='UNHCR Registered'))
    second_child = Child.objects.create(first_name='أحمد', father_name='خالد', last_name='حسن', gender='Male',
                                        birthday_year='2013', nationality=syrian)
    other_child = Child.objects.create(first_name='Other', father_name='Partner', last_name='Child')

    registration = m.Registration.objects.create(child=child, partner=partner, center=center, round=current)
    second = m.Registration.objects.create(child=second_child, partner=partner, center=center, round=current)
    other = m.Registration.objects.create(child=other_child, partner=other_partner, center=other_center,
                                          round=current)
    m.Registration.objects.create(child=child, partner=partner, center=center, round=current, deleted=True)
    return {'registration': registration, 'second': second, 'other': other, 'partner': partner,
            'center': center}


@pytest.fixture
def center_client(client, makani):
    user = get_user_model().objects.create_user(username='center', password='x-pass-123456',
                                                partner=makani['partner'], center=makani['center'])
    for name in ('MSCC', 'MSCC_CENTER'):
        user.groups.add(Group.objects.get_or_create(name=name)[0])
    client.force_login(user)
    return client


@pytest.fixture
def local_media(settings, tmp_path):
    settings.MEDIA_ROOT = str(tmp_path)
    settings.MEDIA_URL = '/media/'
    settings.STORAGES = {
        'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
        'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'},
    }


@pytest.fixture
def queued(monkeypatch):
    calls = []
    monkeypatch.setattr(profile_ids, 'queue_profile_ids',
                        lambda export_id, programme, ids: calls.append((export_id, programme, list(ids))))
    return calls


def test_card_data_matches_registration(makani):
    registration = makani['registration']
    assert registration_profile_id_card(registration) == {
        'round': '2026-2027',
        'id': registration.id,
        'ngo': 'SAVE',
        'full_name': 'ريهام علي الشمق',
        'birthday': '5/5/14',
        'place_of_birth': '',
        'nationality': 'Syrian',
        'governorate': 'Baalbek-Hermel',
        'physical_difficulties': 'No',
        'has_picture': False,
    }
    card = registration_profile_id_card(m.Registration.objects.create(child=makani['second'].child))
    assert card['round'] == '' and card['ngo'] == '' and card['governorate'] == ''
    assert card['birthday'] == '' and card['physical_difficulties'] == 'No'
    assert registration_profile_id_card(m.Registration.objects.create())['full_name'] == ''


def test_pdf_has_one_page_per_child(makani, local_media):
    child = makani['registration'].child
    child.photo.save('child.gif', SimpleUploadedFile('child.gif', GIF, content_type='image/gif'))
    pdf_bytes = build_profile_ids_pdf(MAKANI_PROFILE_IDS.registrations(
        [makani['registration'].id, makani['second'].id]))
    assert _page_count(pdf_bytes) == 2


def test_profile_id_page_renders_card(center_client, makani, local_media):
    registration = makani['registration']
    response = center_client.get('/mscc/child-profile-id/{}/'.format(registration.id))
    assert response.status_code == 200
    html = response.content.decode('utf-8')
    for text in ('2026-2027', 'ID: {}'.format(registration.id), 'NGO: SAVE', 'ريهام علي الشمق',
                 'Date of Birth: 5/5/14', 'Nationality: Syrian', 'Governorate: Baalbek-Hermel',
                 'Physical difficulties: No'):
        assert text in html
    assert '<img' not in html

    registration.child.photo.save('child.gif', SimpleUploadedFile('child.gif', GIF, content_type='image/gif'))
    html = center_client.get('/mscc/child-profile-id/{}/'.format(registration.id)).content.decode('utf-8')
    assert '<img src="/media/child_photos/' in html


def test_profile_page_has_profile_id_button(center_client, makani):
    registration = makani['registration']
    html = center_client.get('/mscc/child-profile/{}/'.format(registration.id)).content.decode('utf-8')
    assert '/mscc/child-profile-id/{}/'.format(registration.id) in html


def test_bulk_profile_ids_queues_visible_children(center_client, makani, queued):
    response = center_client.post('/mscc/profile-ids/')
    assert response.status_code == 200
    export = ExportHistory.objects.get()
    assert response.json() == {'status': 'started', 'export_id': export.id, 'count': 2}
    assert export.export_type == 'Makani Profile IDs'
    assert export.file_format == 'pdf'
    assert export.partner_name == 'SAVE'
    assert export.fields == {'count': 2, 'filters': {}}
    assert len(queued) == 1
    assert queued[0][0] == export.id and queued[0][1] is MAKANI_PROFILE_IDS
    assert sorted(queued[0][2]) == sorted([makani['registration'].id, makani['second'].id])

    response = center_client.post('/mscc/profile-ids/?child__first_name=أحمد')
    assert response.json()['count'] == 1
    assert queued[-1][2] == [makani['second'].id]

    response = center_client.post('/mscc/profile-ids/?ids={},999999'.format(makani['registration'].id))
    assert queued[-1][2] == [makani['registration'].id]

    response = center_client.post('/mscc/profile-ids/?child__first_name=nobody')
    assert response.status_code == 400
    assert center_client.get('/mscc/profile-ids/').status_code == 405


def test_bulk_profile_ids_unicef_sees_every_partner(client, makani, queued):
    user = get_user_model().objects.create_user(username='unicef', password='x-pass-123456')
    for name in ('MSCC', 'MSCC_UNICEF'):
        user.groups.add(Group.objects.get_or_create(name=name)[0])
    client.force_login(user)
    assert client.post('/mscc/profile-ids/').json()['count'] == 3


def test_generate_profile_ids_stores_pdf_and_notifies(makani, monkeypatch):
    saved = {}

    class FakeStorage(object):
        def save(self, name, content):
            saved[name] = content.read()
            return name

    pushes = []
    monkeypatch.setattr(profile_ids, 'ExportStorage', FakeStorage)
    monkeypatch.setattr(profile_ids, 'send_push_to_web',
                        lambda user, title, body, data=None: pushes.append((user, title, body, data)) or True)
    owner = get_user_model().objects.create_user(username='owner')
    export = ExportHistory.objects.create(export_type='Makani Profile IDs', created_by=owner)

    file_url = profile_ids.generate_profile_ids(export.id, MAKANI_PROFILE_IDS,
                                                [makani['registration'].id, makani['second'].id])
    export.refresh_from_db()
    assert export.status == 'done'
    assert export.file_url == file_url
    assert re.match(r'^/mscc/profile-ids/download/profile_ids_[0-9a-f-]+[.]pdf/$', file_url)
    assert _page_count(saved[file_url.split('/')[-2]]) == 2
    assert pushes == [(owner, 'Makani profile IDs ready', 'The PDF with 2 profile ID card(s) is ready to download.',
                       {'type': 'profile_ids_ready', 'label': 'Makani', 'url': file_url, 'export_id': export.id})]


def test_profile_ids_pages_require_login(client, makani):
    registration = makani['registration']
    for url in ('/mscc/child-profile-id/{}/'.format(registration.id),
                '/mscc/profile-ids/download/profile_ids_0f1e2d3c-4b5a-6978-8a9b-0c1d2e3f4a5b.pdf/'):
        assert client.get(url).status_code == 302
    assert client.post('/mscc/profile-ids/').status_code == 302


def test_list_page_links_to_bulk_profile_ids(center_client, makani):
    response = center_client.get('/mscc/list/')
    assert response.status_code == 200
    html = response.content.decode('utf-8')
    assert 'data-url="/mscc/profile-ids/"' in html
    assert 'Generate Profile IDs (PDF)' in html
    assert '/mscc/child-profile-id/{}/'.format(makani['registration'].id) in html
