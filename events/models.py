from decimal import Decimal

from django.conf import settings
from django.db import models
from django.db.models import F, Q


class Event(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Не опубликовано"
        PUBLISHED = "published", "Опубликовано"
        CANCELED = "canceled", "Отменено"
        COMPLETED = "completed", "Завершено"

    title = models.CharField(max_length=100)
    description = models.TextField()
    start_at = models.DateTimeField()
    end_at = models.DateTimeField()
    address = models.TextField()
    max_attendees = models.IntegerField(blank=True, null=True)
    price = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal("0.00")
    )
    organizer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="organized_events",
    )
    status = models.CharField(
        max_length=15, choices=Status.choices, default=Status.DRAFT
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=Q(price__gte=0),
                name="event_price_non_negative",
            ),
            models.CheckConstraint(
                condition=Q(max_attendees__isnull=True) | Q(max_attendees__gt=0),
                name="event_max_attendees_positive",
            ),
            models.CheckConstraint(
                condition=Q(end_at__gt=F("start_at")),
                name="event_end_after_start",
            ),
        ]


class Registration(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Ожидает оплаты"
        CONFIRMED = "confirmed", "Подтверждена"
        CANCELED = "canceled", "Отменена"
        ATTENDED = "attended", "Посетил"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="event_registrations",
    )

    event = models.ForeignKey(
        Event,
        on_delete=models.PROTECT,
        related_name="registrations",
    )

    registered_at = models.DateTimeField(auto_now_add=True)

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )

    bonus_used = models.BooleanField(default=False)

    bonus_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    reminder_sent = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "event"],
                condition=~Q(status="canceled"),
                name="unique_active_registration",
            ),
            models.CheckConstraint(
                condition=Q(bonus_amount__gte=0),
                name="registration_bonus_non_negative",
            ),
            models.CheckConstraint(
                condition=(
                    Q(bonus_used=True, bonus_amount__gt=0)
                    | Q(bonus_used=False, bonus_amount=0)
                ),
                name="registration_bonus_consistency",
            ),
        ]

    def __str__(self):
        return f"{self.user_id} - {self.event_id} ({self.status})"


class Review(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="event_reviews",
    )

    event = models.ForeignKey(
        Event,
        on_delete=models.PROTECT,
        related_name="reviews",
    )

    rating = models.IntegerField()
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=Q(rating__gte=1) & Q(rating__lte=5),
                name="review_rating_between_1_and_5",
            ),
            models.UniqueConstraint(
                fields=["user", "event"],
                name="unique_user_event_review",
            ),
        ]

    def __str__(self):
        return f"Review {self.rating}/5 for event {self.event_id}"
