from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from events.exceptions import RegistrationError
from events.models import Event
from events.serializers import (
    EventCreateSerializer,
    EventListSerializer,
    RegistrationSerializer,
)
from events.services import EventService


class EventViewSet(
    mixins.ListModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet
):
    def get_queryset(self):
        return EventService.get_available_events()

    def get_serializer_class(self):
        if self.action == "create":
            return EventCreateSerializer
        elif self.action == "register":
            return RegistrationSerializer
        return EventListSerializer

    def get_permissions(self):
        if self.action in ["create", "register"]:
            return [IsAuthenticated()]

        return [AllowAny()]

    def perform_create(self, serializer):
        serializer.save(organizer=self.request.user)

    @action(detail=True, methods=["post"])
    def register(self, request, pk=None):
        try:
            registration = EventService.register_user_for_event(
                user=request.user, event_id=pk
            )

        except RegistrationError as exc:
            raise ValidationError({"detail": str(exc)}) from exc

        except Event.DoesNotExist as exc:
            raise NotFound("Мероприятие не найдено") from exc

        serializer = self.get_serializer(registration)
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)
