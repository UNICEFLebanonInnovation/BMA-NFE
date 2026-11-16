"""MEHE media scope, service provisioning and mount-origin behaviour."""
import io
import tempfile
from pathlib import Path
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.files.base import ContentFile
from django.core.management import call_command, CommandError
from django.test import SimpleTestCase, TestCase, override_settings
from rest_framework.authtoken.models import Token

from student_registration.child.models import Child
from student_registration.locations.models import Center
from student_registration.mscc.models import Registration, Round
from student_registration.schools.models import PartnerOrganization
from student_registration.mehe_mounts import remote_share_mount

class MountOriginTests(SimpleTestCase):
    def check_mount(self, kind, source, expected='192.168.41.31'):
        data='31 20 0:40 / /mnt/nfe-media rw - {} {} rw\n'.format(kind,source)
        with patch('pathlib.Path.read_text',return_value=data):
            return remote_share_mount('/mnt/nfe-media',expected)

    def test_smb_share_server_is_verified(self):
        self.assertEqual(self.check_mount('cifs','//192.168.41.31/nfe')['filesystem'],'cifs')

    def test_nfs_share_server_is_verified(self):
        self.assertEqual(self.check_mount('nfs4','192.168.41.31:/exports/nfe')['server'],'192.168.41.31')

    def test_local_bind_directory_is_rejected(self):
        with self.assertRaises(OSError): self.check_mount('ext4','/dev/sda')

    def test_different_remote_server_is_rejected(self):
        with patch('socket.getaddrinfo',return_value=[(2,1,6,'',('192.168.41.99',0))]):
            with self.assertRaises(OSError): self.check_mount('cifs','//other-host/nfe')

    def test_missing_mount_is_rejected(self):
        with patch('pathlib.Path.read_text',return_value=''):
            with self.assertRaises(OSError): remote_share_mount('/mnt/nfe-media','192.168.41.31')

class ServiceClientTests(TestCase):
    def test_service_is_non_login_and_token_is_reused(self):
        call_command('datasync_create_client',username='test-compiler-service',stdout=io.StringIO())
        user=get_user_model().objects.get(username='test-compiler-service')
        self.assertFalse(user.is_staff); self.assertFalse(user.is_superuser)
        self.assertFalse(user.has_usable_password())
        self.assertTrue(user.groups.filter(name='DataSync').exists())
        key=Token.objects.get(user=user).key
        output=io.StringIO()
        call_command('datasync_create_client',username='test-compiler-service',stdout=output)
        self.assertEqual(Token.objects.get(user=user).key,key)
        self.assertIn(key,output.getvalue())

    def test_existing_human_account_is_preserved(self):
        user=get_user_model().objects.create_user(username='existing-human',password='synthetic')
        original=user.password
        with self.assertRaises(CommandError):
            call_command('datasync_create_client',username='existing-human',stdout=io.StringIO())
        user.refresh_from_db(); self.assertEqual(user.password,original)
        self.assertFalse(Token.objects.filter(user=user).exists())

@override_settings(ROOT_URLCONF='config.mehe_urls',NFE_MEDIA_X_ACCEL_REDIRECT=False)
class PhotoAccessTests(TestCase):
    def setUp(self):
        self.folder=tempfile.TemporaryDirectory(); self.addCleanup(self.folder.cleanup)
        self.storage_settings=override_settings(STORAGES={
            'default':{'BACKEND':'django.core.files.storage.FileSystemStorage','OPTIONS':{'location':self.folder.name,'base_url':'/media/'}},
            'staticfiles':{'BACKEND':'django.contrib.staticfiles.storage.StaticFilesStorage'},
        })
        self.storage_settings.enable();self.addCleanup(self.storage_settings.disable)
        self.partner=PartnerOrganization.objects.create(name='Synthetic MEHE partner')
        self.center=Center.objects.create(name='Synthetic MEHE centre',partner=self.partner)
        self.round=Round.objects.create(name='Synthetic MEHE round',year=2026)
        self.child=Child.objects.create(first_name='Synthetic',last_name='MEHE',unicef_id='MEHE-TEST-PHOTO')
        self.child.photo.save('synthetic.png',ContentFile(b'synthetic-photo-bytes'),save=True)
        Registration.objects.create(child=self.child,center=self.center,partner=self.partner,round=self.round,type='Core-Package')
        self.url=self.child.photo.url

    def actor(self, name, group=None, **fields):
        user=get_user_model().objects.create_user(username=name,password='synthetic',**fields)
        if group: user.groups.add(Group.objects.get_or_create(name=group)[0])
        self.client.force_login(user)
        return user

    def test_anonymous_request_requires_login(self):
        self.assertEqual(self.client.get(self.url).status_code,302)

    def test_mehe_role_can_read_saved_photo(self):
        self.actor('mehe-role','MSCC_MEHE')
        response=self.client.get(self.url)
        self.assertEqual(response.status_code,200)
        self.assertEqual(b''.join(response.streaming_content),b'synthetic-photo-bytes')
        self.assertEqual(response['Cache-Control'],'private, no-store')

    def test_matching_partner_can_read_photo(self):
        self.actor('matching-partner','MSCC_PARTNER',partner=self.partner)
        self.assertEqual(self.client.get(self.url).status_code,200)

    def test_other_partner_cannot_read_photo(self):
        other=PartnerOrganization.objects.create(name='Other partner')
        self.actor('other-partner','MSCC_PARTNER',partner=other)
        self.assertEqual(self.client.get(self.url).status_code,404)

    def test_matching_center_can_read_photo(self):
        self.actor('matching-centre','MSCC_CENTER',center=self.center)
        self.assertEqual(self.client.get(self.url).status_code,200)

    def test_unrelated_login_cannot_read_photo(self):
        self.actor('unrelated-login')
        self.assertEqual(self.client.get(self.url).status_code,404)

    def test_data_sync_service_cannot_browse_photos(self):
        self.actor('service-login','DataSync')
        self.assertEqual(self.client.get(self.url).status_code,404)

    def test_x_accel_is_returned_only_after_authorization(self):
        self.actor('mehe-nginx','MSCC_MEHE')
        with self.settings(NFE_MEDIA_X_ACCEL_REDIRECT=True):
            response=self.client.get(self.url)
        self.assertEqual(response.status_code,200)
        self.assertTrue(response['X-Accel-Redirect'].startswith('/_nfe_private_media/child_photos/'))

    def test_missing_file_is_not_reported_as_success(self):
        self.actor('mehe-missing','MSCC_MEHE')
        self.child.photo.storage.delete(self.child.photo.name)
        self.assertEqual(self.client.get(self.url).status_code,404)

    def test_share_failure_returns_retryable_service_status(self):
        self.actor('mehe-storage','MSCC_MEHE')
        with patch('django.core.files.storage.filesystem.FileSystemStorage.exists',side_effect=OSError('share unavailable')):
            self.assertEqual(self.client.get(self.url).status_code,503)

    def test_unreferenced_retained_photo_is_not_public(self):
        self.actor('mehe-old-photo','MSCC_MEHE')
        old=self.url
        self.child.photo='';self.child.save(update_fields=['photo'])
        self.assertEqual(self.client.get(old).status_code,404)
