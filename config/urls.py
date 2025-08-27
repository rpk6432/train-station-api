from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/user/", include("user.urls", namespace="user")),
    path("api/station/", include("station.urls", namespace="station")),
    path("api/order/", include("order.urls", namespace="order")),
]
