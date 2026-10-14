from decimal import Decimal

from django.utils import timezone
from rest_framework import serializers

from .models import Event, Registration


class EventListSerializer(serializers.ModelSerializer):
    current_attendees = serializers.IntegerField(read_only=True)
    average_rating = serializers.FloatField(read_only=True)
    is_full = serializers.BooleanField(read_only=True)

    class Meta:
        model = Event
        fields = [
            "id",
            "title",
            "description",
            "start_at",
            "end_at",
            "address",
            "max_attendees",
            "price",
            "organizer",
            "current_attendees",
            "average_rating",
            "is_full",
        ]


class EventCreateSerializer(serializers.ModelSerializer):
    max_attendees = serializers.IntegerField(
        min_value=1, allow_null=True, required=False
    )
    price = serializers.DecimalField(
        max_digits=10, decimal_places=2, min_value=Decimal("0.00"), required=False
    )

    class Meta:
        model = Event
        fields = [
            "id",
            "title",
            "description",
            "start_at",
            "end_at",
            "address",
            "max_attendees",
            "price",
        ]

    def validate(self, attrs):
        if attrs["start_at"] >= attrs["end_at"]:
            raise serializers.ValidationError(
                {"end_at": "Время окончания должно быть позже начала"}
            )

        if attrs["start_at"] <= timezone.now():
            raise serializers.ValidationError(
                {"start_at": "Дата мероприятия должна быть в будущем"}
            )

        return attrs


class RegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Registration
        fields = [
            "id",
            "event",
            "status",
            "bonus_used",
            "bonus_amount",
            "registered_at",
        ]
        read_only_fields = fields
