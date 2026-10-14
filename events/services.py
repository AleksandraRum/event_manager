from datetime import timedelta
from decimal import Decimal

from django.db import transaction
from django.db.models import Avg, BooleanField, Case, Count, F, Q, Value, When
from django.db.models.functions import Coalesce
from django.utils import timezone

from users.models import User

from .exceptions import RegistrationError
from .models import Event, Registration


class EventService:
    @staticmethod
    @transaction.atomic
    def register_user_for_event(user, event_id):
        locked_event = Event.objects.select_for_update().get(id=event_id)
        locked_user = User.objects.select_for_update().get(id=user.id)

        if locked_event.status != Event.Status.PUBLISHED:
            raise RegistrationError("Событие не опубликовано")
        if locked_event.end_at <= timezone.now():
            raise RegistrationError("Событие уже завершлось")
        if locked_event.organizer_id == locked_user.id:
            raise RegistrationError("Вы организатор этого мероприятия")

        if (
            Registration.objects.filter(
                event_id=locked_event.id, user_id=locked_user.id
            )
            .exclude(status=Registration.Status.CANCELED)
            .exists()
        ):
            raise RegistrationError("Вы уже зарегистрированы на это мероприятие")

        confirmed_attendees = Registration.objects.filter(
            event_id=locked_event.id,
            status=Registration.Status.CONFIRMED,
        ).count()

        if (
            locked_event.max_attendees is not None
            and confirmed_attendees >= locked_event.max_attendees
        ):
            raise RegistrationError("Нет свободных мест")

        registration_status = Registration.Status.PENDING
        registration_bonus_used = False
        registration_bonus_amount = Decimal("0.00")

        if locked_event.price == 0:
            registration_status = Registration.Status.CONFIRMED
            User.objects.filter(id=locked_event.organizer_id).update(
                bonus_balance=F("bonus_balance") + 5
            )

        elif locked_event.price > 0 and locked_user.bonus_balance >= locked_event.price:
            locked_user.bonus_balance -= locked_event.price
            locked_user.save(update_fields=["bonus_balance"])
            registration_status = Registration.Status.CONFIRMED
            registration_bonus_used = True
            registration_bonus_amount = locked_event.price

        registration = Registration.objects.create(
            user=locked_user,
            event=locked_event,
            status=registration_status,
            bonus_used=registration_bonus_used,
            bonus_amount=registration_bonus_amount,
        )
        return registration

    @staticmethod
    @transaction.atomic
    def cancel_registration(user, registration_id):
        registration = Registration.objects.select_for_update().get(
            id=registration_id, user=user
        )

        if registration.status == Registration.Status.CANCELED:
            raise ValueError("Эта регистрацяи уже отменена")

        if timezone.now() + timedelta(days=2) > registration.event.start_at:
            raise ValueError(
                "До мероприятия осталось менее двух суток, отмена не возможна"
            )

        if registration.bonus_used:
            User.objects.filter(id=user.id).update(
                bonus_balance=F("bonus_balance") + registration.bonus_amount
            )

        registration.status = Registration.Status.CANCELED
        registration.save(update_fields=["status"])

        return registration

    @staticmethod
    def get_available_events():
        events = Event.objects.filter(
            status=Event.Status.PUBLISHED, end_at__gt=timezone.now()
        )
        events = events.annotate(
            current_attendees=Count(
                "registrations",
                filter=Q(
                    registrations__status=Registration.Status.CONFIRMED,
                ),
                distinct=True,
            ),
            average_rating=Coalesce(Avg("reviews__rating"), 0.0),
            is_full=Case(
                When(
                    current_attendees__gte=F("max_attendees"),
                    max_attendees__isnull=False,
                    then=Value(True),
                ),
                default=Value(False),
                output_field=BooleanField(),
            ),
        )
        return events
