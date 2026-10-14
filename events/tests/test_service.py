from datetime import timedelta
from decimal import Decimal

import pytest
from django.utils import timezone

from events.exceptions import RegistrationError
from events.models import Event, Registration, Review
from events.services import EventService
from users.models import User


@pytest.fixture
def user_factory():
    def create_user(username, bonus_balance=Decimal("0.00")):
        return User.objects.create_user(
            username=username,
            password="test12345",
            bonus_balance=bonus_balance,
        )

    return create_user


@pytest.mark.django_db
def test_organizer_cannot_register(user_factory):
    user = user_factory("organizer")

    start_at = timezone.now() + timedelta(days=7)

    event = Event.objects.create(
        title="test",
        description="test",
        start_at=start_at,
        end_at=start_at + timedelta(hours=3),
        address="test",
        max_attendees=20,
        price=Decimal("100.00"),
        organizer=user,
        status=Event.Status.PUBLISHED,
    )

    with pytest.raises(RegistrationError, match="Вы организатор этого мероприятия"):
        EventService.register_user_for_event(user=user, event_id=event.id)


@pytest.mark.django_db
def test_cannot_register_when_event_is_full(user_factory):
    organizer = user_factory("organizer")
    user1 = user_factory("user1")
    user2 = user_factory("user2")

    start_at = timezone.now() + timedelta(days=7)

    event = Event.objects.create(
        title="test",
        description="test",
        start_at=start_at,
        end_at=start_at + timedelta(hours=3),
        address="test",
        max_attendees=1,
        price=Decimal("0.00"),
        organizer=organizer,
        status=Event.Status.PUBLISHED,
    )

    Registration.objects.create(
        user=user1,
        event=event,
        status=Registration.Status.CONFIRMED,
        bonus_used=False,
        bonus_amount=Decimal("0.00"),
    )

    with pytest.raises(RegistrationError, match="Нет свободных мест"):
        EventService.register_user_for_event(user=user2, event_id=event.id)


@pytest.mark.django_db
def test_cancel_registration_refunds_bonus(user_factory):
    organizer = user_factory("organizer")
    participant = user_factory(
        "participant",
        bonus_balance=Decimal("150.00"),
    )
    start_at = timezone.now() + timedelta(days=7)

    event = Event.objects.create(
        title="test",
        description="test",
        start_at=start_at,
        end_at=start_at + timedelta(hours=3),
        address="test",
        max_attendees=1,
        price=Decimal("100.00"),
        organizer=organizer,
        status=Event.Status.PUBLISHED,
    )

    registration = EventService.register_user_for_event(
        user=participant,
        event_id=event.id,
    )

    participant.refresh_from_db()
    assert participant.bonus_balance == Decimal("50.00")

    EventService.cancel_registration(
        user=participant,
        registration_id=registration.id,
    )

    participant.refresh_from_db()
    assert participant.bonus_balance == Decimal("150.00")


@pytest.mark.django_db
def test_event_average_rating(user_factory):
    organizer = user_factory("organizer")

    start_at = timezone.now() + timedelta(days=7)

    event = Event.objects.create(
        title="Rating test",
        description="Test average rating",
        start_at=start_at,
        end_at=start_at + timedelta(hours=3),
        address="Test address",
        max_attendees=10,
        price=Decimal("0.00"),
        organizer=organizer,
        status=Event.Status.PUBLISHED,
    )

    user1 = user_factory("user1")
    user2 = user_factory("user2")
    user3 = user_factory("user3")

    Review.objects.create(
        user=user1,
        event=event,
        rating=3,
        text="Нормально",
    )

    Review.objects.create(
        user=user2,
        event=event,
        rating=4,
        text="Хорошо",
    )

    Review.objects.create(
        user=user3,
        event=event,
        rating=5,
        text="Отлично",
    )

    events = EventService.get_available_events()

    event_with_rating = events.get(id=event.id)
    assert event_with_rating.average_rating == 4.0
