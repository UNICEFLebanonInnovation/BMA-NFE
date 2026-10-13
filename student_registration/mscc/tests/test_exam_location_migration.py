"""Check that existing examination answers survive linked-location upgrades."""

from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import TransactionTestCase

from student_registration.locations.models import Location, LocationType


class ExceptionalExamLocationMigrationTests(TransactionTestCase):
    migrate_from = ('mscc', '0021_exceptional_exam')
    migrate_to = ('mscc', '0022_link_exceptional_exam_locations')

    def migrate(self, targets):
        executor = MigrationExecutor(connection)
        executor.migrate(targets)
        return executor.loader.project_state(targets).apps

    def setUp(self):
        super().setUp()
        self.latest_migrations = MigrationExecutor(connection).loader.graph.leaf_nodes()
        self.addCleanup(self.migrate, self.latest_migrations)
        self.old_apps = self.migrate([self.migrate_from])
        self.old_exam = self.old_apps.get_model('mscc', 'ExceptionalExam')
        self.old_registration = self.old_apps.get_model('mscc', 'Registration')

        for pk, name in ((1, 'Governorate'), (2, 'District'), (3, 'Cadaster')):
            LocationType.objects.create(pk=pk, name=name)
        # Arabic alone and English alone both identify the original codes.
        self.governorate = Location.objects.create(name='بيروت', type_id=1)
        self.district = Location.objects.create(name='بيروت', type_id=2, parent=self.governorate)
        self.other_governorate = Location.objects.create(name='Existing Mount Lebanon', name_en='Mount Lebanon', type_id=1)
        self.keserwan = Location.objects.create(
            name='Existing Keserwan', name_en='Keserwan', type_id=2, parent=self.other_governorate,
        )
        # Normalized separators map the database spelling to the attachment.
        self.north = Location.objects.create(name='الشمال', name_en='North', type_id=1)
        self.minnieh_dannieh = Location.objects.create(
            name='المنية الضنية', type_id=2, parent=self.north,
        )
        self.bekaa = Location.objects.create(name='البقاع', name_en='Bekaa', type_id=1)
        self.old_baalbek = Location.objects.create(name='بعلبك', name_en='Baalbek', type_id=2, parent=self.bekaa)
        Location.objects.create(name='زحلة', name_en='Rashaya', type_id=2, parent=self.bekaa)
        conflicting_governorate = Location.objects.create(name='الجنوب', name_en='Nabatieh', type_id=1)
        Location.objects.create(name='النبطية', name_en='Nabatieh', type_id=2, parent=conflicting_governorate)
        # The same label under another governorate must never be selected.
        self.wrong_parent_district = Location.objects.create(
            name='Beirut', type_id=2, parent=self.other_governorate,
        )
        # An identically named location of the wrong type cannot be a governorate.
        Location.objects.create(name='الجنوب', name_en='South Lebanon', type_id=2)
        Location.objects.create(name='صيدا', name_en='Sidon', type_id=3, parent=self.governorate)
        for suffix in ('1', '2'):
            Location.objects.create(name='عكار', name_en='Akkar', type_id=1, p_code='G' + suffix)
            Location.objects.create(
                name='بعبدا', name_en='Baabda', type_id=2,
                parent=self.other_governorate, p_code='D' + suffix,
            )

    def create_old_exam(self, **updates):
        values = dict(
            registration=self.old_registration.objects.create(),
            governorate='beirut', district='beirut', nearest_town='achrafieh',
            programme='BLN', grade='2', math_language='ar', language_exam='en',
        )
        values.update(updates)
        return self.old_exam.objects.create(**values)

    def test_mapping_is_typed_unambiguous_parent_scoped_and_retains_legacy_answers(self):
        original = {
            'Arabic': ('beirut', 'beirut', 'achrafieh'),
            'English': ('mount_lebanon', 'keserwan', 'jounieh'),
            'Separators': ('north_lebanon', 'minnieh_dannieh', 'minnieh'),
            'Unknown': ('unknown_governorate', 'unknown_district', 'unknown_village'),
            'Wrong parent': ('beirut', 'keserwan', 'jounieh'),
            'Ambiguous governorate': ('akkar', 'akkar', 'halba'),
            'Ambiguous district': ('mount_lebanon', 'baabda', 'hadath'),
            'Wrong types': ('south_lebanon', 'sidon', 'sidon'),
            'Conflicting bilingual governorate': ('nabatieh', 'nabatieh', 'nabatieh'),
            'Conflicting bilingual district': ('bekaa', 'zahle', 'zahle'),
            'Different existing boundaries': ('baalbek_hermel', 'baalbek', 'douris'),
        }
        exam_ids = {
            label: self.create_old_exam(
                governorate=values[0], district=values[1], nearest_town=values[2],
            ).pk for label, values in original.items()
        }
        registrations = {
            label: self.old_exam.objects.get(pk=pk).registration_id for label, pk in exam_ids.items()
        }
        location_count = Location.objects.count()

        apps = self.migrate([self.migrate_to])
        Exam = apps.get_model('mscc', 'ExceptionalExam')
        expected = {
            'Arabic': (self.governorate.pk, self.district.pk),
            'English': (self.other_governorate.pk, self.keserwan.pk),
            'Separators': (self.north.pk, self.minnieh_dannieh.pk),
            'Unknown': (None, None),
            'Wrong parent': (self.governorate.pk, None),
            'Ambiguous governorate': (None, None),
            'Ambiguous district': (self.other_governorate.pk, None),
            'Wrong types': (None, None),
            'Conflicting bilingual governorate': (None, None),
            'Conflicting bilingual district': (self.bekaa.pk, None),
            'Different existing boundaries': (None, None),
        }
        self.assertEqual(Location.objects.count(), location_count)
        for label, pk in exam_ids.items():
            with self.subTest(label=label):
                exam = Exam.objects.get(pk=pk)
                self.assertEqual((exam.governorate_id, exam.district_id), expected[label])
                self.assertEqual(
                    (exam.governorate_legacy, exam.district_legacy, exam.nearest_town),
                    original[label],
                )
                self.assertEqual(exam.registration_id, registrations[label])
                self.assertEqual((exam.programme, exam.grade, exam.math_language, exam.language_exam), ('BLN', '2', 'ar', 'en'))

        Exam.objects.filter(pk=exam_ids['Arabic']).update(
            governorate_id=self.other_governorate.pk, district_id=self.keserwan.pk,
            nearest_town='jounieh', grade='7',
        )
        new_exam = Exam.objects.create(
            registration_id=self.old_registration.objects.create().pk,
            governorate_id=self.north.pk, district_id=self.minnieh_dannieh.pk,
            nearest_town='minnieh', programme='DIRASA', grade='6',
            math_language='fr', language_exam='fr',
        )
        apps = self.migrate([self.migrate_from])
        Exam = apps.get_model('mscc', 'ExceptionalExam')
        for label, pk in exam_ids.items():
            with self.subTest(rollback=label):
                exam = Exam.objects.get(pk=pk)
                expected_codes = original[label]
                if label == 'Arabic':
                    expected_codes = ('mount_lebanon', 'keserwan', 'jounieh')
                    self.assertEqual(exam.grade, '7')
                self.assertEqual((exam.governorate, exam.district, exam.nearest_town), expected_codes)
        exam = Exam.objects.get(pk=new_exam.pk)
        self.assertEqual((exam.governorate, exam.district, exam.nearest_town), ('north_lebanon', 'minnieh_dannieh', 'minnieh'))
        self.assertEqual((exam.programme, exam.grade, exam.math_language, exam.language_exam), ('DIRASA', '6', 'fr', 'fr'))

    def test_upgrade_with_no_location_catalogue_keeps_all_saved_answers(self):
        # Use historical models while the examination table is at 0021: the
        # current deletion collector would try to clear FKs not created yet.
        self.old_apps.get_model('locations', 'Location').objects.all().delete()
        self.old_apps.get_model('locations', 'LocationType').objects.all().delete()
        saved = self.create_old_exam()
        apps = self.migrate([self.migrate_to])
        Exam = apps.get_model('mscc', 'ExceptionalExam')
        exam = Exam.objects.get(pk=saved.pk)
        self.assertEqual((exam.governorate_id, exam.district_id), (None, None))
        self.assertEqual((exam.governorate_legacy, exam.district_legacy, exam.nearest_town), ('beirut', 'beirut', 'achrafieh'))
        self.assertEqual(Location.objects.count(), 0)
        self.assertEqual(LocationType.objects.count(), 0)
        apps = self.migrate([self.migrate_from])
        exam = apps.get_model('mscc', 'ExceptionalExam').objects.get(pk=saved.pk)
        self.assertEqual((exam.governorate, exam.district, exam.nearest_town), ('beirut', 'beirut', 'achrafieh'))

    def test_rollback_preserves_latest_custom_location_names_instead_of_stale_codes(self):
        saved = self.create_old_exam()
        apps = self.migrate([self.migrate_to])
        Exam = apps.get_model('mscc', 'ExceptionalExam')
        governorate = Location.objects.create(name='Latest custom governorate', type_id=1)
        district = Location.objects.create(name='Latest custom district', type_id=2, parent=governorate)
        Exam.objects.filter(pk=saved.pk).update(governorate_id=governorate.pk, district_id=district.pk)
        new_exam = Exam.objects.create(
            registration_id=self.old_registration.objects.create().pk,
            governorate_id=governorate.pk, district_id=district.pk,
            nearest_town='achrafieh', programme='BLN', grade='2',
            math_language='ar', language_exam='en',
        )
        apps = self.migrate([self.migrate_from])
        Exam = apps.get_model('mscc', 'ExceptionalExam')
        for pk in (saved.pk, new_exam.pk):
            with self.subTest(exam=pk):
                exam = Exam.objects.get(pk=pk)
                self.assertEqual((exam.governorate, exam.district), (governorate.name, district.name))
        apps = self.migrate([self.migrate_to])
        Exam = apps.get_model('mscc', 'ExceptionalExam')
        for pk in (saved.pk, new_exam.pk):
            with self.subTest(reapply=pk):
                exam = Exam.objects.get(pk=pk)
                self.assertEqual((exam.governorate_id, exam.district_id), (governorate.pk, district.pk))

    def test_long_latest_names_keep_location_identity_across_rollback_and_reapply(self):
        saved = self.create_old_exam()
        apps = self.migrate([self.migrate_to])
        Exam = apps.get_model('mscc', 'ExceptionalExam')
        governorate = Location.objects.create(name='Long current governorate ' * 8, type_id=1)
        district = Location.objects.create(name='Long current district ' * 8, type_id=2, parent=governorate)
        Exam.objects.filter(pk=saved.pk).update(governorate_id=governorate.pk, district_id=district.pk)
        apps = self.migrate([self.migrate_from])
        exam = apps.get_model('mscc', 'ExceptionalExam').objects.get(pk=saved.pk)
        self.assertEqual(exam.governorate, '@location:%s' % governorate.pk)
        self.assertEqual(exam.district, '@location:%s' % district.pk)
        self.assertLessEqual(len(exam.governorate), 64)
        self.assertLessEqual(len(exam.district), 64)

        apps = self.migrate([self.migrate_to])
        exam = apps.get_model('mscc', 'ExceptionalExam').objects.get(pk=saved.pk)
        self.assertEqual((exam.governorate_id, exam.district_id), (governorate.pk, district.pk))
        self.assertEqual((exam.nearest_town, exam.programme, exam.grade), ('achrafieh', 'BLN', '2'))

    def test_rollback_markers_are_restored_only_for_typed_locations_in_the_correct_parent(self):
        def marker(location):
            return '@location:%s' % location.pk

        cases = (
            (marker(self.governorate), marker(self.district), (self.governorate.pk, self.district.pk)),
            (marker(self.district), marker(self.district), (None, None)),
            (marker(self.governorate), marker(self.governorate), (self.governorate.pk, None)),
            (marker(self.governorate), marker(self.keserwan), (self.governorate.pk, None)),
            ('@location:missing', marker(self.district), (None, None)),
            ('@location:999999999', marker(self.district), (None, None)),
        )
        exams = [self.create_old_exam(governorate=gov, district=district).pk for gov, district, _ in cases]
        apps = self.migrate([self.migrate_to])
        Exam = apps.get_model('mscc', 'ExceptionalExam')
        for pk, (governorate_code, district_code, expected) in zip(exams, cases):
            with self.subTest(governorate=governorate_code, district=district_code):
                exam = Exam.objects.get(pk=pk)
                self.assertEqual((exam.governorate_id, exam.district_id), expected)
                self.assertEqual((exam.governorate_legacy, exam.district_legacy), (governorate_code, district_code))

    def test_explicitly_selected_duplicate_governorate_retains_exact_identity_after_rollback(self):
        governors = list(Location.objects.filter(type_id=1, name_en='Akkar').order_by('pk'))
        self.assertEqual(len(governors), 2)
        selected = governors[1]
        district = Location.objects.create(name='عكار', name_en='Akkar', type_id=2, parent=selected)
        saved = self.create_old_exam(governorate='akkar', district='akkar', nearest_town='halba')
        apps = self.migrate([self.migrate_to])
        Exam = apps.get_model('mscc', 'ExceptionalExam')
        exam = Exam.objects.get(pk=saved.pk)
        # The original ambiguous code must not select either governorate.
        self.assertEqual((exam.governorate_id, exam.district_id), (None, None))
        Exam.objects.filter(pk=saved.pk).update(governorate_id=selected.pk, district_id=district.pk)

        apps = self.migrate([self.migrate_from])
        exam = apps.get_model('mscc', 'ExceptionalExam').objects.get(pk=saved.pk)
        self.assertEqual(exam.governorate, '@location:%s' % selected.pk)
        apps = self.migrate([self.migrate_to])
        exam = apps.get_model('mscc', 'ExceptionalExam').objects.get(pk=saved.pk)
        self.assertEqual((exam.governorate_id, exam.district_id), (selected.pk, district.pk))
        self.assertEqual(exam.nearest_town, 'halba')

    def test_explicitly_selected_duplicate_district_retains_exact_identity_after_rollback(self):
        districts = [Location.objects.create(
            name='المتن', name_en='Metn', type_id=2,
            parent=self.other_governorate, p_code=code,
        ) for code in ('METN-1', 'METN-2')]
        selected = districts[1]
        saved = self.create_old_exam(governorate='mount_lebanon', district='metn', nearest_town='jdeideh')
        apps = self.migrate([self.migrate_to])
        Exam = apps.get_model('mscc', 'ExceptionalExam')
        exam = Exam.objects.get(pk=saved.pk)
        self.assertEqual((exam.governorate_id, exam.district_id), (self.other_governorate.pk, None))
        Exam.objects.filter(pk=saved.pk).update(district_id=selected.pk)

        apps = self.migrate([self.migrate_from])
        exam = apps.get_model('mscc', 'ExceptionalExam').objects.get(pk=saved.pk)
        self.assertEqual(exam.governorate, 'mount_lebanon')
        self.assertEqual(exam.district, '@location:%s' % selected.pk)
        apps = self.migrate([self.migrate_to])
        exam = apps.get_model('mscc', 'ExceptionalExam').objects.get(pk=saved.pk)
        self.assertEqual((exam.governorate_id, exam.district_id), (self.other_governorate.pk, selected.pk))
        self.assertEqual(exam.nearest_town, 'jdeideh')

    def test_selected_existing_boundary_district_code_name_round_trips_without_guessing_old_code(self):
        # A raw name identical to a catalogue code still belongs to the real
        # Location parent. The document places Baalbek in another governorate.
        Location.objects.filter(pk=self.old_baalbek.pk).update(name='baalbek', name_en='')
        saved = self.create_old_exam(governorate='bekaa', district='baalbek', nearest_town='douris')
        apps = self.migrate([self.migrate_to])
        Exam = apps.get_model('mscc', 'ExceptionalExam')
        exam = Exam.objects.get(pk=saved.pk)
        self.assertEqual((exam.governorate_id, exam.district_id), (self.bekaa.pk, None))
        Exam.objects.filter(pk=saved.pk).update(district_id=self.old_baalbek.pk)

        apps = self.migrate([self.migrate_from])
        exam = apps.get_model('mscc', 'ExceptionalExam').objects.get(pk=saved.pk)
        self.assertEqual(exam.governorate, 'bekaa')
        self.assertEqual(exam.district, '@location:%s' % self.old_baalbek.pk)
        apps = self.migrate([self.migrate_to])
        exam = apps.get_model('mscc', 'ExceptionalExam').objects.get(pk=saved.pk)
        self.assertEqual((exam.governorate_id, exam.district_id), (self.bekaa.pk, self.old_baalbek.pk))
        self.assertEqual(exam.nearest_town, 'douris')

