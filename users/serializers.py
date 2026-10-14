from rest_framework import serializers

from events.serializers import RegistrationSerializer

from .models import User


class ProfileSerializer(serializers.ModelSerializer):
    registrations = serializers.SerializerMethodField()

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

    def get_registrations(self, obj):
        registrations = self.context["registrations"]
        return RegistrationSerializer(registrations, many=True).data
