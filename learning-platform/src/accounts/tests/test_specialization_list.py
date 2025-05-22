import pytest
from rest_framework import status
from accounts.models import Specialization


@pytest.mark.django_db
class TestSpecializationViewSet:
    """
    Test suite for the SpecializationViewSet.
    """

    def test_list_specializations_ok(
        self, api_client, specialization_url, specializations
    ):
        """
        Test listing all specializations.
        """

        response = api_client.get(specialization_url)
        data = response.data["data"]
        list_name = [specializations.name for specializations in specializations]

        assert response.status_code == status.HTTP_200_OK
        assert len(data) == 2
        assert data[0]["name"] in list_name
        assert data[1]["name"] in list_name

    def test_list_specializations_empty(self, api_client, specialization_url):
        """
        Test listing specializations when there are no specializations.
        """

        Specialization.objects.all().delete()
        response = api_client.get(specialization_url)
        data = response.data["data"]

        assert response.status_code == status.HTTP_200_OK
        assert data == []

    def test_specialization_viewset_permissions(self, api_client, specialization_url):
        """
        Test that the SpecializationViewSet allows any user to access the list of specializations.
        """

        api_client.logout()
        response = api_client.get(specialization_url)

        assert response.status_code == status.HTTP_200_OK

    def test_list_specializations_with_limit_offset(
        self, api_client, specialization_url, specializations
    ):
        """
        Test that specializations are listed in alphabetical order by default.
        """

        response = api_client.get(f"{specialization_url}?limit=5&offset=1")
        data = response.data["data"]
        list_name = [specializations.name for specializations in specializations]
        pagination = response.data["meta"]["pagination"]

        assert response.status_code == status.HTTP_200_OK
        assert len(data) == 1
        assert data[0]["name"] in list_name
        assert pagination["limit"] == 5
        assert pagination["offset"] == 1
        assert pagination["total"] == 2

    def test_list_specializations_failed(self, api_client, root_url):
        """
        Test that the request to list specializations fails due to an invalid URL.
        """

        invalid_url = f"{root_url}invalid_specializations/"
        response = api_client.get(invalid_url)

        assert response.status_code == status.HTTP_404_NOT_FOUND
