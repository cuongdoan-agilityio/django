from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

from accounts.factories import UserFactory
from core.constants import Gender
from students.models import Student
from instructors.models import Instructor, Subject
import uuid

User = get_user_model()


class UserViewSetTests(APITestCase):
    """
    Unit tests for the UserViewSet class.
    """

    def setUp(self):
        """
        Set up the test data.
        """

        self.password = "Password@1234"
        self.student_email = "student@example.com"
        self.instructor_email = "instructor@example.com"

        self.subject = Subject.objects.create(name="Mathematics")

        self.student_user = UserFactory(
            email=self.student_email,
            password=self.password,
            gender=Gender.MALE.value,
        )
        self.student_profile = Student.objects.create(
            user=self.student_user, scholarship=50
        )

        self.instructor_user = UserFactory(
            email=self.instructor_email,
            password=self.password,
        )
        self.instructor_profile = Instructor.objects.create(
            user=self.instructor_user, degree="no"
        )

        self.retrieve_url = "/api/v1/users/me/"

    def test_retrieve_student_profile(self):
        """
        Test the retrieve action for a student.
        """
        self.client.login(email=self.student_email, password=self.password)
        response = self.client.get(self.retrieve_url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_instructor_profile(self):
        """
        Test the retrieve action for an instructor.
        """
        self.client.login(email=self.instructor_email, password=self.password)
        response = self.client.get(self.retrieve_url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_partial_update_student_profile(self):
        """
        Test the partial_update action for a student.
        """
        self.client.login(email=self.student_email, password=self.password)
        data = {
            "phone_number": "0985457215",
            "scholarship": 75,
            "date_of_birth": "1990-01-01",
        }
        response = self.client.patch(
            f"/api/v1/users/{self.student_user.uuid}/", data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_partial_update_student_profile_with_invalid_data(self):
        """
        Test the partial_update action for a student with invalid data.
        """
        self.client.login(email=self.student_email, password=self.password)
        data = {
            "phone_number": "0985457215",
            "scholarship": 75,
            "date_of_birth": "1910-01-01",
        }
        response = self.client.patch(
            f"/api/v1/users/{self.student_user.uuid}/", data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_partial_update_instructor_profile(self):
        """
        Test the partial_update action for an instructor.
        """
        self.client.login(email=self.instructor_email, password=self.password)
        data = {
            "phone_number": "0998712157",
            "degree": "master",
            "date_of_birth": "1985-01-01",
            "subjects": [self.subject.uuid],
        }
        response = self.client.patch(
            f"/api/v1/users/{self.instructor_user.uuid}/", data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_partial_update_instructor_profile_with_invalid_data(self):
        """
        Test the partial_update action for an instructor with invalid data.
        """

        self.client.login(email=self.instructor_email, password=self.password)
        data = {
            "phone_number": "0998712157",
            "degree": "master",
            "date_of_birth": "1900-01-01",
            "subjects": [str(uuid.uuid4())],
        }
        response = self.client.patch(
            f"/api/v1/users/{self.instructor_user.uuid}/", data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_partial_update_instructor_profile_forbidden(self):
        """
        Test the partial_update action for an instructor with forbidden.
        """

        self.client.login(email=self.instructor_email, password=self.password)
        data = {"subjects": [str(uuid.uuid4())]}
        response = self.client.patch(
            f"/api/v1/users/{str(uuid.uuid4())}/", data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
