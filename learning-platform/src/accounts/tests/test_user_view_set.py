import uuid
from rest_framework import status
from core.tests.base import BaseTestCase


class UserViewSetTests(BaseTestCase):
    """
    Unit tests for the UserViewSet class.
    """

    def setUp(self):
        """
        Set up the test data.
        """

        super().setUp()

        self.retrieve_url = f"{self.root_url}users/me/"

    def test_retrieve_student_profile(self):
        """
        Test the retrieve action for a student.
        """

        response = self.get_json(url=self.retrieve_url, email=self.email)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_instructor_profile(self):
        """
        Test the retrieve action for an instructor.
        """

        response = self.get_json(url=self.retrieve_url, email=self.instructor_email)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_partial_update_student_profile(self):
        """
        Test the partial_update action for a student.
        """

        data = {
            "phone_number": self.random_user_phone_number(),
            "scholarship": self.random_scholarship(),
            "date_of_birth": self.random_date_of_birth(is_student=True),
        }

        response = self.patch_json(
            url=f"{self.root_url}users/{self.student_user.uuid}/",
            email=self.email,
            data=data,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_partial_update_student_profile_with_invalid_email(self):
        """
        Test the partial_update action for a student with invalid email.
        """

        data = {
            "phone_number": self.random_user_phone_number(),
            "scholarship": self.random_scholarship(),
            "date_of_birth": "1910-01-01",
        }

        response = self.patch_json(
            url=f"{self.root_url}users/{self.student_user.uuid}/",
            email=self.email,
            data=data,
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_partial_update_instructor_profile(self):
        """
        Test the partial_update action for an instructor.
        """

        data = {
            "phone_number": self.random_user_phone_number(),
            "degree": self.random_degree(),
            "date_of_birth": self.random_date_of_birth(is_student=False),
            "subjects": [self.subject.uuid],
        }

        response = self.patch_json(
            url=f"{self.root_url}users/{self.instructor_user.uuid}/",
            email=self.instructor_email,
            data=data,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_partial_update_instructor_profile_with_invalid_subjects(self):
        """
        Test the partial_update action for an instructor with invalid subject.
        """

        data = {
            "phone_number": self.random_user_phone_number(),
            "degree": self.random_degree(),
            "date_of_birth": self.random_date_of_birth(is_student=False),
            "subjects": [str(uuid.uuid4())],
        }

        response = self.patch_json(
            url=f"{self.root_url}users/{self.instructor_user.uuid}/",
            email=self.instructor_email,
            data=data,
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_partial_update_instructor_profile_forbidden(self):
        """
        Test the partial_update action for an instructor with forbidden.
        """

        data = {"subjects": [str(uuid.uuid4())]}

        response = self.patch_json(
            url=f"{self.root_url}users/{str(uuid.uuid4())}/",
            email=self.instructor_email,
            data=data,
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
