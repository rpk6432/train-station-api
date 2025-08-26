from django.urls import path, include
from rest_framework import routers
from .views import StationViewSet, TrainTypeViewSet, CrewViewSet, RouteViewSet

app_name = "station"

router = routers.DefaultRouter()
router.register("stations", StationViewSet, basename="station")
router.register("train-types", TrainTypeViewSet, basename="train-type")
router.register("crews", CrewViewSet, basename="crew")
router.register("routes", RouteViewSet, basename="route")

urlpatterns = [path("", include(router.urls))]
