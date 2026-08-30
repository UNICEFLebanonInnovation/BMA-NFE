from student_registration.mscc.serializers import MainSerializer

from .models import ALPRegistration


class ALPRegistrationSerializer(MainSerializer):
    """MSCC-compatible child serializer backed by an ALP registration."""

    class Meta(MainSerializer.Meta):
        model = ALPRegistration
        fields = MainSerializer.Meta.fields + (
            'school', 'round', 'programme', 'registration_date', 'student_old',
        )
