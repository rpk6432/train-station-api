from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from station.models import Journey


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders",
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Order {self.id} by {self.user}"


class Ticket(models.Model):
    cargo = models.PositiveIntegerField()
    seat = models.PositiveIntegerField()
    journey = models.ForeignKey(
        Journey, on_delete=models.CASCADE, related_name="tickets"
    )
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="tickets"
    )

    class Meta:
        unique_together = ("journey", "cargo", "seat")
        ordering = ["cargo", "seat"]

    def clean(self):
        if not (1 <= self.cargo <= self.journey.train.cargo_num):
            raise ValidationError(
                {
                    "cargo": f"Cargo number must be between 1 and {self.journey.train.cargo_num}."
                }
            )

        if not (1 <= self.seat <= self.journey.train.places_in_cargo):
            raise ValidationError(
                {
                    "seat": f"Seat number must be between 1 and {self.journey.train.places_in_cargo}."
                }
            )

    def __str__(self):
        return f"{self.journey} (Cargo: {self.cargo}, Seat: {self.seat})"
