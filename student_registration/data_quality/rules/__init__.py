"""Initial deterministic MSCC rule registrations."""

from .child import (
    BirthDateIsRealRule,
    BirthDateNotFutureRule,
    ChildCountPositiveRule,
    ChildCountZeroRule,
    DisabilityOtherRequiredRule,
    IdentityConfirmationRule,
    NationalityOtherRequiredRule,
    PhoneConfirmationRule,
)
from .registration import (
    CashProgrammeSelectionRule,
    RegistrationChildRequiredRule,
    RegistrationPartnerCenterRule,
)

__all__ = (
    "BirthDateIsRealRule",
    "BirthDateNotFutureRule",
    "CashProgrammeSelectionRule",
    "ChildCountPositiveRule",
    "ChildCountZeroRule",
    "DisabilityOtherRequiredRule",
    "IdentityConfirmationRule",
    "NationalityOtherRequiredRule",
    "PhoneConfirmationRule",
    "RegistrationChildRequiredRule",
    "RegistrationPartnerCenterRule",
)
