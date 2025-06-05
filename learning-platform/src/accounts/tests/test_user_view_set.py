import uuid
from rest_framework import status
from .base import BaseAccountModuleTestCase


class TestUserViewSet(BaseAccountModuleTestCase):
    """
    Test suite for the UserViewSet.
    """

    fragment = "users/"

    def test_retrieve_student_profile(self):
        """
        Test the retrieve action for a student.
        """

        response = self.get_json(f"{self.fragment}me/")

        assert response.status_code == status.HTTP_200_OK

    def test_retrieve_student_profile_with_id(self):
        """
        Test the retrieve action for a student.
        """

        response = self.get_json(f"{self.fragment}{str(self.fake_student.id)}/")

        assert response.status_code == status.HTTP_200_OK

    def test_retrieve_instructor_profile(self):
        """
        Test the retrieve action for an instructor.
        """

        self.authenticated_token = self.fake_instructor_token
        response = self.get_json(f"{self.fragment}me/")

        assert response.status_code == status.HTTP_200_OK

    def test_retrieve_instructor_profile_with_id(self):
        """
        Test the retrieve action for a student.
        """

        self.authenticated_token = self.fake_instructor_token
        response = self.get_json(f"{self.fragment}{str(self.fake_instructor.id)}/")

        assert response.status_code == status.HTTP_200_OK

    def test_retrieve_user_profile_with_invalid_id(self):
        """
        Test the retrieve action for a student.
        """

        self.authenticated_token = self.fake_instructor_token
        response = self.get_json(f"{self.fragment}{str(self.fake_student.id)}/")

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_admin_retrieve_user_profile_with_invalid_id(self):
        """
        Test the retrieve action for a student.
        """

        self.authenticated_token = self.fake_admin_token
        response = self.get_json(f"{self.fragment}{str(uuid.uuid4())}/")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_partial_update_student_profile(self):
        """
        Test the partial_update action for a student.
        """

        data = {
            "phone_number": "1234567890",
            "scholarship": self.random_scholarship,
            "date_of_birth": "2000-01-01",
        }
        response = self.patch_json(f"{self.fragment}{self.fake_student.id}/", data)
        self.fake_student.refresh_from_db()

        assert response.status_code == status.HTTP_200_OK
        assert self.fake_student.phone_number == data.get("phone_number")
        assert self.fake_student.scholarship == data.get("scholarship")
        assert self.fake_student.date_of_birth.strftime("%Y-%m-%d") == data.get(
            "date_of_birth"
        )

    def test_partial_update_student_profile_with_invalid_data(self):
        """
        Test the partial_update action for a student with invalid dob.
        """

        url = f"{self.fragment}{self.fake_student.id}/"
        data = {
            "phone_number": "1234567890",
            "scholarship": "Full",
            "date_of_birth": "1910-01-01",
        }
        response = self.patch_json(url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_partial_update_instructor_profile(self):
        """
        Test the partial_update action for an instructor.
        """

        data = {
            "phone_number": "0854215785",
            "degree": self.random_degree,
            "date_of_birth": "1980-01-01",
            "specializations": [self.fake_specialization.id],
        }
        self.authenticated_token = self.fake_instructor_token
        response = self.patch_json(f"{self.fragment}{self.fake_instructor.id}/", data)

        assert response.status_code == status.HTTP_200_OK

    def test_partial_update_instructor_profile_with_invalid_specializations(self):
        """
        Test the partial_update action for an instructor with invalid specialization.
        """

        self.authenticated_token = self.fake_instructor_token
        data = {
            "phone_number": "1234567890",
            "degree": "PhD",
            "date_of_birth": "1980-01-01",
            "specializations": [str(uuid.uuid4())],
        }
        response = self.patch_json(f"{self.fragment}{self.fake_instructor.id}/", data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_partial_update_instructor_profile_not_found(self):
        """
        Test the partial_update action for an instructor with a non-existent user.
        """

        self.authenticated_token = self.fake_instructor_token
        data = {"specializations": [str(uuid.uuid4())]}
        response = self.patch_json(f"{self.fragment}{str(uuid.uuid4())}/", data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_partial_update_user_profile_with_invalid_id(self):
        """
        Test the partial_update action for an instructor with a non-existent user.
        """

        self.authenticated_token = self.fake_instructor_token
        data = {"phone_number": "1234567890"}
        response = self.patch_json(f"{self.fragment}{str(self.fake_student.id)}/", data)

        assert response.status_code == status.HTTP_403_FORBIDDEN
