import pytest
from rest_framework import status
from accounts.factories import SpecializationFactory
from accounts.models import Specialization
from .base import BaseAccountModuleTestCase


class TestSpecializationViewSet(BaseAccountModuleTestCase):
    """
    Test suite for the SpecializationViewSet.
    """

    fragment = "specializations/"

    @pytest.fixture(autouse=True)
    def init_specializations(self, setup, db):
        """
        Fixture to create sample specializations.
        """

        self.specializations = [
            SpecializationFactory(),
            SpecializationFactory(),
        ]

    def test_list_specializations_ok(self):
        """
        Test listing all specializations.
        """

        response = self.get_json(fragment=self.fragment)
        data = response.data["data"]
        list_name = [item.name for item in self.specializations]

        assert response.status_code == status.HTTP_200_OK
        assert data[0]["name"] in list_name
        assert data[1]["name"] in list_name

    def test_list_specializations_empty(self):
        """
        Test listing specializations when there are no specializations.
        """

        Specialization.objects.all().delete()
        response = self.get_json(fragment=self.fragment)
        data = response.data["data"]

        assert response.status_code == status.HTTP_200_OK
        assert data == []

    def test_specialization_viewset_permissions(self):
        """
        Test that the SpecializationViewSet allows any user to access the list of specializations.
        """
        self.auth = None
        response = self.get_json(fragment=self.fragment)

        assert response.status_code == status.HTTP_200_OK

    def test_list_specializations_with_limit_offset(self):
        """
        Test that specializations are listed in alphabetical order by default.
        """

        response = self.get_json(f"{self.fragment}?limit=5&offset=1")
        data = response.data["data"]
        list_name = [item.name for item in self.specializations]
        pagination = response.data["meta"]["pagination"]

        assert response.status_code == status.HTTP_200_OK
        assert len(data) == 2
        assert data[0]["name"] in list_name
        assert pagination["limit"] == 5
        assert pagination["offset"] == 1
        assert pagination["total"] == 3

    def test_list_specializations_failed(self):
        """
        Test that the request to list specializations fails due to an invalid URL.
        """

        invalid_url = f"{self.root_url}invalid_specializations/"
        response = self.get_json(invalid_url)

        assert response.status_code == status.HTTP_404_NOT_FOUND
