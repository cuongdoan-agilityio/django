from rest_framework import status
from courses.models import Category
from courses.factories import CategoryFactory
from courses.api.serializers import CategorySerializer
from core.tests.base import BaseTestCase


class CategoryViewSetTest(BaseTestCase):
    """
    Test case for the CategoryViewSet.
    """

    def setUp(self):
        """
        Set up the test case with sample categories.
        """
        super().setUp()

        CategoryFactory()
        self.url = f"{self.root_url}categories/"

    def test_list_categories_success(self):
        """
        Test listing all categories.
        """

        response = self.client.get(self.url)
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"], serializer.data)

    def test_list_categories_empty_success(self):
        """
        Test listing categories when there are no categories.
        """

        Category.objects.all().delete()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"], [])

    def test_category_viewset_permissions(self):
        """
        Test that the CategoryViewSet allows any user to access the list of categories.
        """

        self.client.logout()
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_categories_failed(self):
        """
        Test listing categories with an incorrect endpoint.
        """

        incorrect_url = f"{self.root_url}incorrect_categories/"
        response = self.client.get(incorrect_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
