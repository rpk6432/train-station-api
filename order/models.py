from django.conf import settings
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
    cargo = models.IntegerField()
    seat = models.IntegerField()
    journey = models.ForeignKey(
        Journey, on_delete=models.CASCADE, related_name="tickets"
    )
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="tickets"
    )

    class Meta:
        unique_together = ("journey", "cargo", "seat")
        ordering = ["cargo", "seat"]

    def __str__(self):
        return f"{self.journey} (Cargo: {self.cargo}, Seat: {self.seat})"
