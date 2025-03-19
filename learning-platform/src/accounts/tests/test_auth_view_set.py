from rest_framework import status
from core.tests.base import BaseTestCase


class AuthorViewSetTests(BaseTestCase):
    def setUp(self):
        super().setUp()

        self.login_url = f"{self.root_url}auth/login/"
        self.signup = f"{self.root_url}auth/signup/"

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
            "username": self.fake.user_name(),
            "first_name": self.fake.first_name(),
            "last_name": self.fake.last_name(),
            "email": self.fake.email(),
            "password": "Newpassword@123",
            "phone_number": self.random_user_phone_number(),
            "date_of_birth": self.random_date_of_birth(is_student=True),
            "gender": self.random_gender(),
            "scholarship": self.random_scholarship(),
        }
        response = self.client.post(self.signup, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_signup_with_invalid_username(self):
        """
        Test the signup action with invalid user name.
        """

        data = {
            "username": self.username,
            "email": self.email,
            "password": self.password,
        }
        response = self.client.post(self.signup, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_signup_with_invalid_email(self):
        """
        Test the signup action with invalid email.
        """

        data = {
            "username": self.fake.user_name(),
            "email": self.email,
            "password": self.password,
        }
        response = self.client.post(self.signup, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
