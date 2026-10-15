from rest_framework import serializers

from events.serializers import RegistrationSerializer
from users.models import User


class ProfileSerializer(serializers.ModelSerializer):
    registrations = RegistrationSerializer(
        source="latest_registrations",
        many=True,
        read_only=True,
    )

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "phone_number",
            "bonus_balance",
            "registrations",
        ]
