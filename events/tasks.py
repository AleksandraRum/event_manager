from datetime import timedelta

from celery import shared_task
from django.utils import timezone

from .models import Event, Registration


@shared_task
def send_event_reminders():
    now = timezone.now()

    window_start = now + timedelta(hours=24)
    window_end = now + timedelta(hours=25)

    registrations = Registration.objects.filter(
        status=Registration.Status.CONFIRMED,
        reminder_sent=False,
        event__status=Event.Status.PUBLISHED,
        event__start_at__gte=window_start,
        event__start_at__lt=window_end,
    ).select_related("user", "event")

    for registration in registrations:
        print(
            f"Напоминание пользователю {registration.user.username}: "
            f"мероприятие '{registration.event.title}' "
            f"начнётся {registration.event.start_at}"
        )

        registration.reminder_sent = True
        registration.save(update_fields=["reminder_sent"])
