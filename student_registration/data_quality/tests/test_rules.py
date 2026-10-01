from datetime import date, timedelta

from django.test import TestCase

from student_registration.clm.models import Disability
from student_registration.data_quality.rules.child import (
    BirthDateIsRealRule,
    BirthDateNotFutureRule,
    ChildCountPositiveRule,
    ChildCountZeroRule,
    DisabilityOtherRequiredRule,
    IdentityConfirmationRule,
    NationalityOtherRequiredRule,
    PhoneConfirmationRule,
)
from student_registration.data_quality.rules.registration import (
    CashProgrammeSelectionRule,
    RegistrationChildRequiredRule,
    RegistrationPartnerCenterRule,
)
from student_registration.tests.factories import (
    CenterFactory,
    ChildFactory,
    NationalityFactory,
    PartnerOrganizationFactory,
    RegistrationFactory,
)


class ChildRuleTests(TestCase):
    def test_invalid_calendar_date_fails_without_storing_birth_values(self):
        child = ChildFactory.build(
            birthday_year="2015",
            birthday_month="2",
            birthday_day="30",
        )

        result = BirthDateIsRealRule()(child)

        self.assertFalse(result.passed)
        self.assertEqual(result.evidence["reason"], "invalid_calendar_date")
        self.assertNotIn("2015", str(result.evidence))

    def test_future_birth_date_fails(self):
        future = date.today() + timedelta(days=1)
        child = ChildFactory.build(
            birthday_year=str(future.year),
            birthday_month=str(future.month),
            birthday_day=str(future.day),
        )

        result = BirthDateNotFutureRule()(child)

        self.assertFalse(result.passed)
        self.assertEqual(result.evidence, {"reason": "future_date"})

    def test_identity_confirmation_reports_field_names_not_identity_values(self):
        child = ChildFactory.build(
            individual_case_number="sensitive-id",
            individual_case_number_confirm="different-id",
        )

        result = IdentityConfirmationRule()(child)

        self.assertFalse(result.passed)
        self.assertIn(
            ["individual_case_number", "individual_case_number_confirm"],
            result.evidence["mismatched_pairs"],
        )
        self.assertNotIn("sensitive-id", str(result.evidence))

    def test_phone_confirmation_reports_field_names_not_phone_values(self):
        child = ChildFactory.build(
            first_phone_number="70000000",
            first_phone_number_confirm="71111111",
        )

        result = PhoneConfirmationRule()(child)

        self.assertFalse(result.passed)
        self.assertNotIn("70000000", str(result.evidence))

    def test_other_nationality_requires_explanation(self):
        child = ChildFactory.build(
            nationality=NationalityFactory.build(name="Other", name_en="Other"),
            nationality_other="",
        )

        self.assertFalse(NationalityOtherRequiredRule()(child).passed)

    def test_other_disability_requires_explanation(self):
        child = ChildFactory.build(
            disability=Disability(name="Other", name_en="Other"),
            disability_other="",
        )

        self.assertFalse(DisabilityOtherRequiredRule()(child).passed)

    def test_no_children_requires_zero_or_empty_count(self):
        child = ChildFactory.build(have_children="No", children_number=2)

        self.assertFalse(ChildCountZeroRule()(child).passed)

    def test_having_children_requires_positive_count(self):
        child = ChildFactory.build(have_children="Yes", children_number=0)

        self.assertFalse(ChildCountPositiveRule()(child).passed)


class RegistrationRuleTests(TestCase):
    def test_none_cash_programme_cannot_be_combined_with_another_value(self):
        registration = RegistrationFactory.build(
            cash_support_programmes=["None", "Haddi"]
        )

        self.assertFalse(CashProgrammeSelectionRule()(registration).passed)

    def test_registration_partner_must_match_center_partner(self):
        partner = PartnerOrganizationFactory()
        different_partner = PartnerOrganizationFactory()
        registration = RegistrationFactory(
            partner=partner,
            center=CenterFactory(partner=different_partner),
        )

        self.assertFalse(RegistrationPartnerCenterRule()(registration).passed)

    def test_registration_requires_child(self):
        registration = RegistrationFactory.build(child=None)

        self.assertFalse(RegistrationChildRequiredRule()(registration).passed)
