from typing import Type

from django.db.models import Count, QuerySet
from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.serializers import Serializer
from .models import Order
from .serializers import (
    OrderSerializer,
    OrderListSerializer,
    OrderDetailSerializer,
)


class OrderViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self) -> QuerySet:
        queryset = self.queryset.filter(user=self.request.user)

        if date := self.request.query_params.get("date"):
            queryset = queryset.filter(created_at__date=date)

        if self.action == "list":
            queryset = queryset.annotate(tickets_count=Count("tickets"))

        if self.action == "retrieve":
            queryset = queryset.prefetch_related(
                "tickets__journey__route__source",
                "tickets__journey__route__destination",
                "tickets__journey__train",
            )
        return queryset

    def get_serializer_class(self) -> Type[Serializer]:
        if self.action == "list":
            return OrderListSerializer
        if self.action == "retrieve":
            return OrderDetailSerializer
        return self.serializer_class

    def perform_create(self, serializer: Serializer) -> None:
        serializer.save(user=self.request.user)
