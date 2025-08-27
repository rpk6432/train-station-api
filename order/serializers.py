from django.db import transaction
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from station.serializers import JourneyListSerializer
from .models import Order, Ticket


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ("id", "cargo", "seat", "journey")
        validators = [
            UniqueTogetherValidator(
                queryset=Ticket.objects.all(),
                fields=("journey", "cargo", "seat"),
                message="This seat is already taken on this journey."
            )
        ]


class TicketDetailSerializer(TicketSerializer):
    journey = JourneyListSerializer(many=False, read_only=True)


class OrderSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True, allow_empty=False)

    class Meta:
        model = Order
        fields = ("id", "tickets", "created_at")

    def validate_tickets(self, tickets):
        if not tickets:
            return tickets

        positions_list = [
            (t["cargo"], t["seat"], t["journey"]) for t in tickets
        ]
        if len(positions_list) != len(set(positions_list)):
            raise serializers.ValidationError("An order cannot contain duplicate tickets.")

        for ticket_data in tickets:
            journey = ticket_data["journey"]
            cargo = ticket_data["cargo"]
            seat = ticket_data["seat"]
            train = journey.train

            if not (1 <= cargo <= train.cargo_num):
                raise serializers.ValidationError(
                    f"Cargo {cargo} is not valid for train {train.name}."
                )
            if not (1 <= seat <= train.places_in_cargo):
                raise serializers.ValidationError(
                    f"Seat {seat} is not valid for train {train.name}."
                )
        return tickets

    @transaction.atomic
    def create(self, validated_data):
        tickets_data = validated_data.pop("tickets")
        order = Order.objects.create(**validated_data)
        for ticket_data in tickets_data:
            Ticket.objects.create(order=order, **ticket_data)
        return order


class OrderListSerializer(OrderSerializer):
    tickets_count = serializers.IntegerField(
        source="tickets.count", read_only=True
    )

    class Meta:
        model = Order
        fields = ("id", "tickets_count", "created_at")


class OrderDetailSerializer(OrderSerializer):
    tickets = TicketDetailSerializer(many=True, read_only=True)
