from django.contrib import admin
from .models import (
    Station,
    Route,
    TrainType,
    Train,
    Crew,
    Journey,
)


@admin.register(Station)
class StationAdmin(admin.ModelAdmin):
    list_display = ("name", "latitude", "longitude")
    search_fields = ("name",)


@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ("source", "destination", "distance")


@admin.register(Train)
class TrainAdmin(admin.ModelAdmin):
    list_display = ("name", "train_type", "cargo_num", "places_in_cargo", "capacity")
    list_filter = ("train_type",)
    search_fields = ("name",)


@admin.register(Journey)
class JourneyAdmin(admin.ModelAdmin):
    list_display = ("route", "train", "departure_time", "arrival_time")
    list_filter = ("route__source", "route__destination", "departure_time")
    search_fields = ("route__source__name", "route__destination__name")


admin.site.register(TrainType)
admin.site.register(Crew)
