import pytest
from rest_framework import status
from courses.models import Category
from courses.api.serializers import CategorySerializer


@pytest.mark.django_db
class TestCategoryViewSet:
    """
    Test suite for the CategoryViewSet.
    """

    def test_list_categories_success(self, api_client, category_url, fake_categories):
        """
        Test listing all categories.
        """

        response = api_client.get(category_url)
        assert response.status_code == status.HTTP_200_OK

        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)

        assert response.data["data"] == serializer.data

    def test_list_categories_empty_success(self, api_client, category_url):
        """
        Test listing categories when there are no categories.
        """

        Category.objects.all().delete()
        response = api_client.get(category_url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["data"] == []

    def test_category_viewset_permissions(self, api_client, category_url):
        """
        Test that the CategoryViewSet allows any user to access the list of categories.
        """

        api_client.logout()
        response = api_client.get(category_url)

        assert response.status_code == status.HTTP_200_OK
