from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.utils import timezone
from datetime import timedelta

from station.models import Station, Route, Train, Journey, TrainType
from order.models import Order
from order.serializers import OrderListSerializer

ORDER_URL = reverse("order:order-list")


def create_sample_journey():
    source = Station.objects.create(name="Source", latitude=1.0, longitude=1.0)
    destination = Station.objects.create(
        name="Destination", latitude=2.0, longitude=2.0
    )
    route = Route.objects.create(
        source=source, destination=destination, distance=100
    )
    train_type = TrainType.objects.create(name="TestType")
    train = Train.objects.create(
        name="TestTrain",
        cargo_num=10,
        places_in_cargo=50,
        train_type=train_type,
    )
    journey = Journey.objects.create(
        route=route,
        train=train,
        departure_time="2025-10-10T10:00:00Z",
        arrival_time="2025-10-10T12:00:00Z",
    )
    return journey


def get_results(response):
    """
    Return the list of items from a DRF list response.

    If the view uses pagination, response.data is a dict containing "results";
    otherwise response.data is the list itself.
    """

    data = response.data
    if isinstance(data, dict) and "results" in data:
        return data["results"]
    return data


class OrderApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@example.com", "password123"
        )
        self.client.force_authenticate(user=self.user)
        self.journey = create_sample_journey()

    def test_list_orders_unauthenticated_fails(self):
        """Test that listing orders requires authentication"""
        self.client.force_authenticate(user=None)
        res = self.client.get(ORDER_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_only_own_orders(self):
        """Test that a user sees only their own orders"""
        another_user = get_user_model().objects.create_user(
            "another@user.com", "pass"
        )
        Order.objects.create(user=another_user)
        own_order = Order.objects.create(user=self.user)

        res = self.client.get(ORDER_URL)
        items = get_results(res)
        serializer = OrderListSerializer([own_order], many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(items), 1)
        self.assertEqual(items, serializer.data)

    def test_create_order_success(self):
        """Test creating an order is successful"""
        payload = {
            "tickets": [
                {"cargo": 1, "seat": 1, "journey": self.journey.id},
                {"cargo": 1, "seat": 2, "journey": self.journey.id},
            ]
        }
        res = self.client.post(ORDER_URL, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        order = Order.objects.get(id=res.data["id"])
        self.assertEqual(order.tickets.count(), 2)
        self.assertEqual(order.user, self.user)

    def test_create_order_with_taken_seat_fails(self):
        """Test error is returned when trying to book a taken seat"""
        another_user = get_user_model().objects.create_user(
            "another@user.com", "pass"
        )
        order = Order.objects.create(user=another_user)
        order.tickets.create(cargo=1, seat=1, journey=self.journey)

        payload = {
            "tickets": [{"cargo": 1, "seat": 1, "journey": self.journey.id}]
        }
        res = self.client.post(ORDER_URL, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_order_success(self):
        """Test retrieving own order with details"""
        order = Order.objects.create(user=self.user)
        order.tickets.create(cargo=1, seat=1, journey=self.journey)

        url = reverse("order:order-detail", args=[order.id])
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["id"], order.id)
        self.assertEqual(len(res.data["tickets"]), 1)

    def test_retrieve_other_user_order_fails(self):
        """Test user cannot retrieve someone else’s order"""
        another_user = get_user_model().objects.create_user(
            "another@user.com", "pass"
        )
        order = Order.objects.create(user=another_user)
        url = reverse("order:order-detail", args=[order.id])

        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_filter_orders_by_date(self):
        """Test filtering orders by created_at date"""
        today = timezone.now().date()
        order_today = Order.objects.create(user=self.user)

        order_yesterday = Order.objects.create(user=self.user)
        Order.objects.filter(id=order_yesterday.id).update(
            created_at=timezone.now() - timedelta(days=1)
        )

        res = self.client.get(ORDER_URL, {"date": str(today)})
        items = get_results(res)
        ids = [o["id"] for o in items]

        self.assertIn(order_today.id, ids)
        self.assertNotIn(order_yesterday.id, ids)

    def test_create_order_with_duplicate_tickets_fails(self):
        """Test creating order with duplicate tickets fails"""
        payload = {
            "tickets": [
                {"cargo": 1, "seat": 1, "journey": self.journey.id},
                {"cargo": 1, "seat": 1, "journey": self.journey.id},
            ]
        }
        res = self.client.post(ORDER_URL, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_order_with_invalid_cargo_or_seat_fails(self):
        """Test creating order with invalid cargo or seat fails"""
        payload = {
            "tickets": [
                {"cargo": 0, "seat": 1, "journey": self.journey.id},
                {"cargo": 1, "seat": 999, "journey": self.journey.id},
            ]
        }
        res = self.client.post(ORDER_URL, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
