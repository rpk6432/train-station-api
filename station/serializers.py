from rest_framework import serializers

from .models import Station, TrainType, Crew, Route, Train, Journey


class StationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Station
        fields = ("id", "name", "latitude", "longitude")


class TrainTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainType
        fields = ("id", "name")


class CrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = ("id", "first_name", "last_name", "full_name")
        read_only_fields = ("full_name",)


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = ("id", "source", "destination", "distance")


class RouteListSerializer(RouteSerializer):
    source = StationSerializer(many=False, read_only=True)
    destination = StationSerializer(many=False, read_only=True)


class TrainSerializer(serializers.ModelSerializer):
    class Meta:
        model = Train
        fields = (
            "id",
            "name",
            "cargo_num",
            "places_in_cargo",
            "train_type",
            "capacity",
            "image",
        )
        read_only_fields = ("capacity",)


class TrainListSerializer(TrainSerializer):
    train_type_name = serializers.CharField(
        source="train_type.name", read_only=True
    )

    class Meta:
        model = Train
        fields = (
            "id",
            "name",
            "cargo_num",
            "places_in_cargo",
            "capacity",
            "train_type_name",
            "image",
        )


class TrainDetailSerializer(TrainSerializer):
    train_type = TrainTypeSerializer(many=False, read_only=True)


class TrainImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Train
        fields = ("id", "image")


class RouteForJourneyDetailSerializer(serializers.ModelSerializer):
    source = serializers.CharField(source="source.name")
    destination = serializers.CharField(source="destination.name")

    class Meta:
        model = Route
        fields = ("id", "source", "destination", "distance")


class TrainForJourneyDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Train
        fields = ("id", "name", "capacity", "image")


class JourneySerializer(serializers.ModelSerializer):
    class Meta:
        model = Journey
        fields = (
            "id",
            "route",
            "train",
            "crew",
            "departure_time",
            "arrival_time",
        )


class JourneyListSerializer(serializers.ModelSerializer):
    route = serializers.StringRelatedField(many=False)
    train_name = serializers.CharField(source="train.name", read_only=True)
    train_capacity = serializers.IntegerField(
        source="train.capacity", read_only=True
    )
    tickets_available = serializers.IntegerField(read_only=True)

    class Meta:
        model = Journey
        fields = (
            "id",
            "route",
            "train_name",
            "train_capacity",
            "tickets_available",
            "departure_time",
            "arrival_time",
        )


class JourneyDetailSerializer(JourneySerializer):
    route = RouteForJourneyDetailSerializer(many=False, read_only=True)
    train = TrainForJourneyDetailSerializer(many=False, read_only=True)
    crew = serializers.StringRelatedField(many=True, read_only=True)
    taken_seats = serializers.SerializerMethodField()
    tickets_available = serializers.IntegerField(read_only=True)

    class Meta:
        model = Journey
        fields = (
            "id",
            "route",
            "train",
            "crew",
            "departure_time",
            "arrival_time",
            "tickets_available",
            "taken_seats",
        )

    def get_taken_seats(self, obj):
        return [
            {"cargo": ticket.cargo, "seat": ticket.seat}
            for ticket in obj.tickets.all()
        ]
