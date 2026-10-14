from decimal import Decimal

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    bonus_balance = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal("0.00")
    )
    phone_number = models.CharField(max_length=20, unique=True, blank=True, null=True)
