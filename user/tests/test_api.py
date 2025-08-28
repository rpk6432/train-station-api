from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from user.serializers import UserSerializer

CREATE_USER_URL = reverse("user:create")
TOKEN_URL = reverse("user:token_obtain_pair")
ME_URL = reverse("user:me")


class UserApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@example.com",
            password="password123",
        )
        self.client.force_authenticate(user=self.user)

    def test_create_user_success(self):
        """Test creating a new user is successful"""
        payload = {
            "email": "new_user@example.com",
            "password": "new_password123",
        }
        res = APIClient().post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(email=payload["email"])
        self.assertTrue(user.check_password(payload["password"]))
        self.assertNotIn("password", res.data)

    def test_create_user_with_existing_email_fails(self):
        """Test error is returned if registering with an existing email"""
        payload = {
            "email": self.user.email,
            "password": "password123",
        }
        res = APIClient().post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_success(self):
        """Test creating a JWT token is successful"""
        payload = {
            "email": self.user.email,
            "password": "password123",
        }
        res = APIClient().post(TOKEN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("access", res.data)
        self.assertIn("refresh", res.data)

    def test_create_token_with_bad_credentials_fails(self):
        """Test getting a token with bad credentials fails"""
        payload = {"email": self.user.email, "password": "wrongpassword"}
        res = APIClient().post(TOKEN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_profile_unauthenticated_fails(self):
        """Test that retrieving a profile unauthenticated fails"""
        res = APIClient().get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_profile_authenticated_success(self):
        """Test retrieving profile for an authenticated user"""
        res = self.client.get(ME_URL)
        serializer = UserSerializer(self.user)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_update_profile_authenticated_success(self):
        """Test updating the profile for an authenticated user"""
        payload = {"first_name": "NewFirstName"}
        res = self.client.patch(ME_URL, payload)
        self.user.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user.first_name, payload["first_name"])

    def test_update_password_authenticated_success(self):
        """Test updating password for an authenticated user"""
        payload = {"password": "newpassword123"}
        res = self.client.patch(ME_URL, payload)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(payload["password"]))
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_update_email_authenticated_success(self):
        """Test updating email for an authenticated user"""
        payload = {"email": "updated@example.com"}
        res = self.client.patch(ME_URL, payload)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, payload["email"])
        self.assertEqual(res.status_code, status.HTTP_200_OK)
