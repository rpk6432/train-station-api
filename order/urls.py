from django.urls import path, include
from rest_framework import routers

from .views import OrderViewSet

app_name = "order"

router = routers.DefaultRouter()
router.register("orders", OrderViewSet, basename="order")

urlpatterns = [path("", include(router.urls))]
