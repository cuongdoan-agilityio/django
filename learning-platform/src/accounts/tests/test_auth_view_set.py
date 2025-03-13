from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model
from core.constants import Gender
from accounts.factories import UserFactory

User = get_user_model()


class AuthorViewSetTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.username = "test_user"
        self.first_name = "Test"
        self.last_name = "User"
        self.email = "test@example.com"
        self.password = "password1234"
        self.phone_number = "1234567890"
        self.date_of_birth = "1990-01-01"
        self.gender = Gender.MALE.value

        self.user = UserFactory(
            email=self.email,
            password=self.password,
        )

        self.token = Token.objects.filter(user=self.user).first()

        self.login_url = "/api/v1/auth/login/"
        self.signup = "/api/v1/auth/signup/"

    def test_login_success(self):
        """
        Test login success.
        """
        data = {
            "email": self.email,
            "password": self.password,
        }
        response = self.client.post(self.login_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_login_failure(self):
        """
        Test login invalid with invalid password.
        """
        data = {"email": self.email, "password": "wrong_password"}
        response = self.client.post(self.login_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_signup(self):
        """
        Test the signup action.
        """
        data = {
            "username": "newuser",
            "first_name": "New",
            "last_name": "User",
            "email": "newuser@example.com",
            "password": "newpassword1234",
            "phone_number": "0987654321",
            "date_of_birth": "2000-01-01",
            "gender": Gender.FEMALE.value,
            "scholarship": 75,
        }
        response = self.client.post(self.signup, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_signup_with_invalid_username(self):
        """
        Test the signup action with invalid user name.
        """
        data = {
            "username": self.username,
            "email": "newuser@example.com",
            "password": self.password,
        }
        response = self.client.post(self.signup, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_signup_with_invalid_email(self):
        """
        Test the signup action with invalid email.
        """
        data = {
            "username": "newuser",
            "email": self.email,
            "password": self.password,
        }
        response = self.client.post(self.signup, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
