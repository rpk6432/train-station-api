from typing import Type

from django.db.models import Count, F, QuerySet
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
)
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.serializers import Serializer

from user.permissions import IsAdminOrReadOnly
from .models import Station, TrainType, Crew, Route, Train, Journey
from .serializers import (
    StationSerializer,
    TrainTypeSerializer,
    CrewSerializer,
    RouteSerializer,
    RouteListSerializer,
    TrainImageSerializer,
    TrainListSerializer,
    TrainSerializer,
    TrainDetailSerializer,
    JourneyListSerializer,
    JourneyDetailSerializer,
    JourneySerializer,
)


class BaseViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = (IsAdminOrReadOnly,)


@extend_schema_view(
    list=extend_schema(summary="List all stations"),
    create=extend_schema(summary="Create a new station (admin only)"),
    retrieve=extend_schema(summary="Retrieve a specific station"),
    update=extend_schema(summary="Update a specific station (admin only)"),
    partial_update=extend_schema(
        summary="Partially update a specific station (admin only)"
    ),
)
class StationViewSet(BaseViewSet):
    queryset = Station.objects.all()
    serializer_class = StationSerializer


@extend_schema_view(
    list=extend_schema(summary="List all train types"),
    create=extend_schema(summary="Create a new train type (admin only)"),
    retrieve=extend_schema(summary="Retrieve a specific train type"),
    update=extend_schema(summary="Update a specific train type (admin only)"),
    partial_update=extend_schema(
        summary="Partially update a specific train type (admin only)"
    ),
)
class TrainTypeViewSet(BaseViewSet):
    queryset = TrainType.objects.all()
    serializer_class = TrainTypeSerializer


@extend_schema_view(
    list=extend_schema(summary="List all crew members"),
    create=extend_schema(summary="Create a new crew member (admin only)"),
    retrieve=extend_schema(summary="Retrieve a specific crew member"),
    update=extend_schema(summary="Update a specific crew member (admin only)"),
    partial_update=extend_schema(
        summary="Partially update a specific crew member (admin only)"
    ),
)
class CrewViewSet(BaseViewSet):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer


@extend_schema_view(
    list=extend_schema(summary="List all routes"),
    create=extend_schema(summary="Create a new route (admin only)"),
    retrieve=extend_schema(summary="Retrieve a specific route"),
    update=extend_schema(summary="Update a specific route (admin only)"),
    partial_update=extend_schema(
        summary="Partially update a specific route (admin only)"
    ),
)
class RouteViewSet(BaseViewSet):
    queryset = Route.objects.select_related("source", "destination")
    serializer_class = RouteSerializer

    def get_serializer_class(self) -> Type[Serializer]:
        if self.action in ("list", "retrieve"):
            return RouteListSerializer
        return self.serializer_class


@extend_schema_view(
    list=extend_schema(summary="List all trains"),
    create=extend_schema(summary="Create a new train (admin only)"),
    retrieve=extend_schema(summary="Retrieve a specific train"),
    update=extend_schema(summary="Update a specific train (admin only)"),
    partial_update=extend_schema(
        summary="Partially update a specific train (admin only)"
    ),
)
class TrainViewSet(BaseViewSet):
    queryset = Train.objects.select_related("train_type")
    serializer_class = TrainSerializer

    def get_serializer_class(self) -> Type[Serializer]:
        if self.action == "list":
            return TrainListSerializer
        if self.action == "retrieve":
            return TrainDetailSerializer
        if self.action == "upload_image":
            return TrainImageSerializer
        return self.serializer_class

    @extend_schema(
        summary="Upload an image to a specific train",
        description=(
            "Endpoint for uploading an image to a specific train. "
            "Only admins can perform this action."
        ),
    )
    @action(
        methods=["POST"],
        detail=True,
        url_path="upload-image",
        permission_classes=[IsAdminUser],
    )
    def upload_image(self, request, pk=None) -> Response:
        train = self.get_object()
        serializer = self.get_serializer(train, data=request.data)

        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema_view(
    list=extend_schema(
        summary="List all journeys",
        description=(
            "Retrieve a list of all available journeys. "
            "Can be filtered by source, destination, and date."
        ),
        parameters=[
            OpenApiParameter(
                name="from",
                type=OpenApiTypes.STR,
                description=(
                    "Filter by source station name or ID "
                    "(e.g., Central Station or 1)."
                ),
            ),
            OpenApiParameter(
                name="to",
                type=OpenApiTypes.STR,
                description=(
                    "Filter by destination station name or ID "
                    "(e.g., North Station or 2)."
                ),
            ),
            OpenApiParameter(
                name="date",
                type=OpenApiTypes.DATE,
                description="Filter by departure date (format: YYYY-MM-DD).",
            ),
        ],
    ),
    create=extend_schema(
        summary="Create a new journey (admin only)",
        description=(
            "Create a new journey for a specific route and train. "
            "Only administrators can perform this action."
        ),
    ),
    retrieve=extend_schema(
        summary="Retrieve a specific journey",
        description=(
            "Retrieve detailed information about a specific journey, "
            "including the route, train, crew, and taken seats."
        ),
    ),
    update=extend_schema(
        summary="Update a specific journey (admin only)",
        description=(
            "Update all details of a specific journey. "
            "Only administrators can perform this action."
        ),
    ),
    partial_update=extend_schema(
        summary="Partially update a specific journey (admin only)",
        description=(
            "Partially update the details of a specific journey. "
            "Only administrators can perform this action."
        ),
    ),
)
class JourneyViewSet(BaseViewSet):
    queryset = Journey.objects.all()
    serializer_class = JourneySerializer

    def get_queryset(self) -> QuerySet:
        queryset = self.queryset

        if source := self.request.query_params.get("from"):
            if source.isdigit():
                queryset = queryset.filter(route__source__id=int(source))
            else:
                queryset = queryset.filter(
                    route__source__name__icontains=source
                )

        if destination := self.request.query_params.get("to"):
            if destination.isdigit():
                queryset = queryset.filter(
                    route__destination__id=int(destination)
                )
            else:
                queryset = queryset.filter(
                    route__destination__name__icontains=destination
                )

        if date := self.request.query_params.get("date"):
            queryset = queryset.filter(departure_time__date=date)

        if self.action == "list":
            queryset = queryset.select_related(
                "route__source", "route__destination", "train"
            ).annotate(
                tickets_available=(
                    F("train__cargo_num") * F("train__places_in_cargo")
                    - Count("tickets")
                )
            )

        if self.action == "retrieve":
            queryset = queryset.select_related(
                "route__source", "route__destination", "train"
            ).prefetch_related("crew", "tickets")

        return queryset

    def get_serializer_class(self) -> Type[Serializer]:
        if self.action == "list":
            return JourneyListSerializer
        if self.action == "retrieve":
            return JourneyDetailSerializer
        return self.serializer_class
