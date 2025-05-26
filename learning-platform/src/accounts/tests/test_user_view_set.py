import pytest
import uuid
from rest_framework import status


@pytest.mark.django_db
class TestUserViewSet:
    """
    Test suite for the UserViewSet.
    """

    # Thanh Nguyen [Presentation]: Create a slide comparing before and after refactoring.
    # Thanh Nguyen [Presentation] [Slide] [Workflow slide]: present the workflow you like best. The remaining flows will be attached with links in the slide.
    # Thanh Nguyen [Presentation]: Slide: Update text font size: Title: 28/30, normal text: 20/24

    def test_retrieve_student_profile(
        self, api_client, authenticated_fake_student, user_retrieve_url
    ):
        """
        Test the retrieve action for a student.
        """

        response = api_client.get(user_retrieve_url)
        assert response.status_code == status.HTTP_200_OK

    def test_retrieve_student_profile_with_id(
        self, api_client, fake_student, authenticated_fake_student, user_url
    ):
        """
        Test the retrieve action for a student.
        """

        response = api_client.get(f"{user_url}{str(fake_student.id)}/")
        assert response.status_code == status.HTTP_200_OK

    def test_retrieve_instructor_profile(
        self, api_client, authenticated_fake_instructor, user_retrieve_url
    ):
        """
        Test the retrieve action for an instructor.
        """

        response = api_client.get(user_retrieve_url)
        assert response.status_code == status.HTTP_200_OK

    def test_retrieve_instructor_profile_with_id(
        self, api_client, fake_instructor, authenticated_fake_instructor, user_url
    ):
        """
        Test the retrieve action for a student.
        """

        response = api_client.get(f"{user_url}{str(fake_instructor.id)}/")
        assert response.status_code == status.HTTP_200_OK

    def test_retrieve_user_profile_with_invalid_id(
        self, api_client, fake_student, authenticated_fake_instructor, user_url
    ):
        """
        Test the retrieve action for a student.
        """

        response = api_client.get(f"{user_url}{str(fake_student.id)}/")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_admin_retrieve_user_profile_with_invalid_id(
        self, api_client, authenticated_fake_admin, user_url
    ):
        """
        Test the retrieve action for a student.
        """

        fake_id = uuid.uuid4()

        response = api_client.get(f"{user_url}{str(fake_id)}/")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_partial_update_student_profile(
        self,
        api_client,
        fake_student,
        authenticated_fake_student,
        random_scholarship,
        user_url,
    ):
        """
        Test the partial_update action for a student.
        """

        data = {
            "phone_number": "1234567890",
            "scholarship": random_scholarship,
            "date_of_birth": "2000-01-01",
        }
        response = api_client.patch(f"{user_url}{fake_student.id}/", data)
        assert response.status_code == status.HTTP_200_OK

        fake_student.refresh_from_db()
        assert fake_student.phone_number == data.get("phone_number")
        assert fake_student.scholarship == data.get("scholarship")
        assert fake_student.date_of_birth.strftime("%Y-%m-%d") == data.get(
            "date_of_birth"
        )

    def test_partial_update_student_profile_with_invalid_data(
        self, api_client, fake_student, authenticated_fake_student, user_url
    ):
        """
        Test the partial_update action for a student with invalid email.
        """

        url = f"{user_url}{fake_student.id}/"
        data = {
            "phone_number": "1234567890",
            "scholarship": "Full",
            "date_of_birth": "1910-01-01",
        }
        response = api_client.patch(url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_partial_update_instructor_profile(
        self,
        api_client,
        fake_instructor,
        authenticated_fake_instructor,
        random_degree,
        specialization,
        user_url,
    ):
        """
        Test the partial_update action for an instructor.
        """

        data = {
            "phone_number": "0854215785",
            "degree": random_degree,
            "date_of_birth": "1980-01-01",
            "specializations": [specialization.id],
        }
        response = api_client.patch(f"{user_url}{fake_instructor.id}/", data)
        assert response.status_code == status.HTTP_200_OK

    def test_partial_update_instructor_profile_with_invalid_specializations(
        self, api_client, fake_instructor, user_url, authenticated_fake_instructor
    ):
        """
        Test the partial_update action for an instructor with invalid specialization.
        """

        data = {
            "phone_number": "1234567890",
            "degree": "PhD",
            "date_of_birth": "1980-01-01",
            "specializations": [str(uuid.uuid4())],
        }
        response = api_client.patch(f"{user_url}{fake_instructor.id}/", data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_partial_update_instructor_profile_not_found(
        self, api_client, user_url, authenticated_fake_instructor
    ):
        """
        Test the partial_update action for an instructor with a non-existent user.
        """

        data = {"specializations": [str(uuid.uuid4())]}
        response = api_client.patch(f"{user_url}{str(uuid.uuid4())}/", data)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_partial_update_user_profile_with_invalid_id(
        self,
        api_client,
        user_url,
        authenticated_fake_instructor,
        fake_student,
    ):
        """
        Test the partial_update action for an instructor with a non-existent user.
        """

        data = {"phone_number": "1234567890"}
        response = api_client.patch(f"{user_url}{str(fake_student.id)}/", data)
        assert response.status_code == status.HTTP_403_FORBIDDEN
