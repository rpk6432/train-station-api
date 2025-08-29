from typing import Type

from django.db.models import Count, QuerySet
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
)
from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.serializers import Serializer
from .models import Order
from .serializers import (
    OrderSerializer,
    OrderListSerializer,
    OrderDetailSerializer,
)


@extend_schema_view(
    list=extend_schema(
        summary="List all orders for the current user",
        description=(
            "Retrieve a list of orders made by the current user. "
            "Can be filtered by creation date."
        ),
        parameters=[
            OpenApiParameter(
                name="date",
                type=OpenApiTypes.DATE,
                description=(
                    "Filter orders by creation date (format: YYYY-MM-DD)."
                ),
            )
        ],
    ),
    create=extend_schema(
        summary="Create a new order",
        description=(
            "Create a new order with a list of tickets. "
            "This action is available only for authenticated users."
        ),
    ),
    retrieve=extend_schema(
        summary="Retrieve a specific order",
        description=(
            "Retrieve the details of a specific order, "
            "including all tickets and their journey information. "
            "Users can only access their own orders."
        ),
    ),
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
