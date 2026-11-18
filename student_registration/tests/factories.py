"""Reusable factories for MSCC QA and data-quality tests.

Keep these factories focused on valid, minimal domain objects. Individual tests
should override only the values relevant to the behavior under test.
"""

import factory
from django.contrib.auth.models import Group
from factory.django import DjangoModelFactory

from student_registration.child.models import Child
from student_registration.locations.models import Center, Location, LocationType
from student_registration.mscc.models import Registration, Round
from student_registration.schools.models import PartnerOrganization
from student_registration.students.models import IDType, Nationality
from student_registration.tests.constants import DATA_QUALITY_REVIEWER_GROUP
from student_registration.users.models import User


class PartnerOrganizationFactory(DjangoModelFactory):
    """Create an active partner with a unique name."""

    class Meta:
        model = PartnerOrganization

    name = factory.Sequence(lambda number: f"QA Partner {number}")
    short_name = factory.Sequence(lambda number: f"QAP{number}")
    active = True


class LocationTypeFactory(DjangoModelFactory):
    """Create a location type suitable for a geographic test hierarchy."""

    class Meta:
        model = LocationType

    name = factory.Sequence(lambda number: f"QA Location Type {number}")
    name_en = factory.LazyAttribute(lambda location_type: location_type.name)


class LocationFactory(DjangoModelFactory):
    """Create a location with a stable, unique P-Code."""

    class Meta:
        model = Location

    name = factory.Sequence(lambda number: f"QA Location {number}")
    name_en = factory.LazyAttribute(lambda location: location.name)
    type = factory.SubFactory(LocationTypeFactory)
    p_code = factory.Sequence(lambda number: f"QA-PCODE-{number}")


class NationalityFactory(DjangoModelFactory):
    """Create a nationality without relying on production fixture IDs."""

    class Meta:
        model = Nationality

    name = factory.Sequence(lambda number: f"QA Nationality {number}")
    name_en = factory.LazyAttribute(lambda nationality: nationality.name)
    code = factory.Sequence(lambda number: f"Q{number:04d}"[-5:])


class IDTypeFactory(DjangoModelFactory):
    """Create an active identity type without relying on hard-coded IDs."""

    class Meta:
        model = IDType

    name = factory.Sequence(lambda number: f"QA Identity Type {number}")
    active = True


class UserFactory(DjangoModelFactory):
    """Create a usable project user with a deterministic test password."""

    class Meta:
        model = User

    username = factory.Sequence(lambda number: f"qa-user-{number}")
    email = factory.LazyAttribute(lambda user: f"{user.username}@example.test")
    partner = factory.SubFactory(PartnerOrganizationFactory)
    is_active = True

    @factory.post_generation
    def password(self, create, extracted, **kwargs):
        self.set_password(extracted or "test-password")
        if create:
            self.save(update_fields=["password"])


class DataQualityReviewerFactory(UserFactory):
    """Create a user assigned to the dedicated data-quality reviewer group."""

    @factory.post_generation
    def reviewer_group(self, create, extracted, **kwargs):
        if not create:
            return
        group, _ = Group.objects.get_or_create(name=DATA_QUALITY_REVIEWER_GROUP)
        self.groups.add(group)


class CenterFactory(DjangoModelFactory):
    """Create an active center owned by a user from the same partner."""

    class Meta:
        model = Center

    partner = factory.SubFactory(PartnerOrganizationFactory)
    owner = factory.SubFactory(
        UserFactory,
        partner=factory.SelfAttribute("..partner"),
    )
    name = factory.Sequence(lambda number: f"QA Center {number}")
    governorate = factory.SubFactory(LocationFactory)
    p_code = factory.Sequence(lambda number: f"QA-CENTER-{number}")
    is_active = True


class ChildFactory(DjangoModelFactory):
    """Create a complete-enough MSCC child for quality and matching tests."""

    class Meta:
        model = Child

    first_name = factory.Sequence(lambda number: f"Child{number}")
    father_name = "Father"
    last_name = "Family"
    mother_fullname = "Mother Family"
    gender = "Female"
    nationality = factory.SubFactory(NationalityFactory)
    birthday_year = "2015"
    birthday_month = "6"
    birthday_day = "15"
    id_type = factory.SubFactory(IDTypeFactory)
    individual_case_number = factory.Sequence(lambda number: f"QA-ID-{number}")
    individual_case_number_confirm = factory.SelfAttribute("individual_case_number")
    first_phone_number = factory.Sequence(lambda number: f"700{number:05d}")
    first_phone_number_confirm = factory.SelfAttribute("first_phone_number")
    caregiver_first_name = "Caregiver"
    caregiver_middle_name = "Parent"
    caregiver_last_name = "Family"
    caregiver_mother_name = "Grandmother Family"
    cash_programmes = factory.LazyFunction(dict)


class RoundFactory(DjangoModelFactory):
    """Create a distinct MSCC implementation round."""

    class Meta:
        model = Round

    name = factory.Sequence(lambda number: f"QA Round {number}")
    year = 2026


class RegistrationFactory(DjangoModelFactory):
    """Create a registration with consistent partner, center, owner, and child."""

    class Meta:
        model = Registration

    partner = factory.SubFactory(PartnerOrganizationFactory)
    center = factory.SubFactory(
        CenterFactory,
        partner=factory.SelfAttribute("..partner"),
    )
    owner = factory.SubFactory(
        UserFactory,
        partner=factory.SelfAttribute("..partner"),
    )
    child = factory.SubFactory(ChildFactory)
    round = factory.SubFactory(RoundFactory)
    deleted = False
