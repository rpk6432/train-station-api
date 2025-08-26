from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from user.permissions import IsAdminOrReadOnly
from .models import Station, TrainType, Crew, Route, Train
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
)


class BaseViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = (IsAdminOrReadOnly,)


class StationViewSet(BaseViewSet):
    queryset = Station.objects.all()
    serializer_class = StationSerializer


class TrainTypeViewSet(BaseViewSet):
    queryset = TrainType.objects.all()
    serializer_class = TrainTypeSerializer


class CrewViewSet(BaseViewSet):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer


class RouteViewSet(BaseViewSet):
    queryset = Route.objects.select_related("source", "destination")
    serializer_class = RouteSerializer

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return RouteListSerializer
        return self.serializer_class


class TrainViewSet(BaseViewSet):
    queryset = Train.objects.select_related("train_type")
    serializer_class = TrainSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return TrainListSerializer
        if self.action == "retrieve":
            return TrainDetailSerializer
        if self.action == "upload_image":
            return TrainImageSerializer
        return self.serializer_class

    @action(
        methods=["POST"],
        detail=True,
        url_path="upload-image",
        permission_classes=[IsAdminUser],
    )
    def upload_image(self, request, pk=None):
        """Endpoint for uploading image to a specific train"""
        train = self.get_object()
        serializer = self.get_serializer(train, data=request.data)

        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
