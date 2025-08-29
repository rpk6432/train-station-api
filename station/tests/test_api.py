import shutil
import tempfile
import os
from PIL import Image
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from station.models import Station, Train, TrainType

STATION_URL = reverse("station:station-list")
TEMP_MEDIA_ROOT = tempfile.mkdtemp()

def detail_url(station_id):
    return reverse("station:station-detail", args=[station_id])

def train_image_upload_url(train_id):
    return reverse("station:train-upload-image", args=[train_id])

def train_detail_url(train_id):
    return reverse("station:train-detail", args=[train_id])

class StationApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@example.com", "password123"
        )
        self.admin_user = get_user_model().objects.create_superuser(
            "admin@example.com", "password123"
        )
        self.station = Station.objects.create(
            name="Station A", latitude=1.0, longitude=1.0
        )

    def test_list_stations_unauthenticated_success(self):
        """Test that listing stations is allowed for unauthenticated users"""
        res = self.client.get(STATION_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_station_unauthenticated_fails(self):
        """Test that creating a station is forbidden for unauthenticated users"""
        payload = {"name": "Test", "latitude": 2.0, "longitude": 2.0}
        res = self.client.post(STATION_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_station_authenticated_user_fails(self):
        """Test that creating a station is forbidden for regular users"""
        self.client.force_authenticate(user=self.user)
        payload = {"name": "Test", "latitude": 2.0, "longitude": 2.0}
        res = self.client.post(STATION_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_station_admin_user_success(self):
        """Test that creating a station is allowed for admin users"""
        self.client.force_authenticate(user=self.admin_user)
        payload = {"name": "Test", "latitude": 2.0, "longitude": 2.0}
        res = self.client.post(STATION_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_retrieve_station_success(self):
        """Test that retrieving a station is allowed for unauthenticated users"""
        url = detail_url(self.station.id)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["id"], self.station.id)

    def test_update_station_authenticated_user_fails(self):
        """Test that updating a station is forbidden for regular users"""
        self.client.force_authenticate(user=self.user)
        payload = {"name": "New Name"}
        url = detail_url(self.station.id)
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_station_admin_user_success(self):
        """Test that updating a station is allowed for admin users"""
        self.client.force_authenticate(user=self.admin_user)
        payload = {"name": "New Name"}
        url = detail_url(self.station.id)
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.station.refresh_from_db()
        self.assertEqual(self.station.name, "New Name")


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class TrainImageUploadTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = get_user_model().objects.create_superuser(
            "admin@example.com", "password123"
        )
        self.train_type = TrainType.objects.create(name="Type 1")
        self.train = Train.objects.create(
            name="Train 1",
            cargo_num=2,
            places_in_cargo=50,
            train_type=self.train_type
        )

    def tearDown(self):
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_upload_image_admin_success(self):
        """Test that admin can upload an image to a train"""
        self.client.force_authenticate(self.admin_user)
        url = train_image_upload_url(self.train.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            res = self.client.post(url, {"image": ntf}, format="multipart")
        self.train.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("image", res.data)
        self.assertTrue(os.path.exists(self.train.image.path))

    def test_image_field_shown_in_detail(self):
        """Test that uploaded image is shown in train detail"""
        self.client.force_authenticate(self.admin_user)
        url_upload = train_image_upload_url(self.train.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            self.client.post(url_upload, {"image": ntf}, format="multipart")
        url_detail = train_detail_url(self.train.id)
        res = self.client.get(url_detail)
        self.assertIn("image", res.data)
