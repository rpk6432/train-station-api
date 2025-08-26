from rest_framework import viewsets, mixins
from user.permissions import IsAdminOrReadOnly
from .models import Station, TrainType, Crew
from .serializers import StationSerializer, TrainTypeSerializer, CrewSerializer


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
