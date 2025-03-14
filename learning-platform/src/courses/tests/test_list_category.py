from rest_framework import status
from rest_framework.test import APITestCase
from categories.models import Category
from categories.factories import CategoryFactory


class CategoryViewSetTest(APITestCase):
    """
    Test case for the CategoryViewSet.
    """

    def setUp(self):
        """
        Set up the test case with sample categories.
        """

        CategoryFactory()
        self.url = "/api/v1/categories/"

    def test_list_categories(self):
        """
        Test listing all categories.
        """

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_categories_empty(self):
        """
        Test listing categories when there are no categories.
        """

        Category.objects.all().delete()
        response = self.client.get(self.url)
        data = response.data["data"]
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data, [])

    def test_category_viewset_permissions(self):
        """
        Test that the CategoryViewSet allows any user to access the list of categories.
        """

        self.client.logout()
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
