from rest_framework import status
from accounts.models import Specialization
from accounts.factories import SpecializationFactory
from core.tests.base import BaseTestCase
from django.core.cache import cache


class SpecializationViewSetTest(BaseTestCase):
    """
    Test case for the SpecializationViewSet.
    """

    def setUp(self):
        """
        Set up the test case with sample specializations.
        """
        super().setUp()

        Specialization.objects.all().delete()
        self.specialization_name = self.fake.sentence(nb_words=5)
        self.another_specialization_name = self.fake.sentence(nb_words=5)
        SpecializationFactory(name=self.specialization_name)
        SpecializationFactory(name=self.another_specialization_name)

        self.url = f"{self.root_url}specializations/"

    def tearDown(self):
        super().tearDown()
        cache.delete("specializations_list")

    def test_list_specializations_ok(self):
        """
        Test listing all specializations.
        """

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data["data"]
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]["name"], self.specialization_name)
        self.assertEqual(data[1]["name"], self.another_specialization_name)

        # Verify that the data is cached
        cached_data = cache.get("specializations_list")
        self.assertIsNotNone(cached_data)
        self.assertEqual(len(cached_data), 2)

    def test_list_specializations_empty(self):
        """
        Test listing specializations when there are no specializations.
        """

        Specialization.objects.all().delete()
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.data["data"]
        self.assertEqual(data, [])

    def test_specialization_viewset_permissions(self):
        """
        Test that the SpecializationViewSet allows any user to access the list of specializations.
        """

        self.client.logout()
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_specializations_with_limit_offset(self):
        """
        Test that specializations are listed in alphabetical order by default.
        """

        response = self.client.get(f"{self.url}?limit=5&offset=1")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.data["data"]
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["name"], self.another_specialization_name)

        pagination = response.data["meta"]["pagination"]
        self.assertEqual(pagination["limit"], 5)
        self.assertEqual(pagination["offset"], 1)
        self.assertEqual(pagination["total"], 2)

    def test_list_specializations_failed(self):
        """
        Test that the request to list specializations fails due to an invalid URL.
        """

        invalid_url = f"{self.root_url}invalid_specializations/"
        response = self.client.get(invalid_url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
