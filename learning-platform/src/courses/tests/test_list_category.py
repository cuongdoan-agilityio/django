from rest_framework import status
from courses.models import Category
from courses.api.serializers import CategorySerializer
from .base import BaseCourseModuleTestCase


class TestCategoryViewSet(BaseCourseModuleTestCase):
    """
    Test suite for the CategoryViewSet.
    """

    fragment = "categories/"

    def test_list_categories_success(self):
        """
        Test listing all categories.
        """

        response = self.get_json(self.fragment)
        assert response.status_code == status.HTTP_200_OK

        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)

        assert response.data["data"] == serializer.data

    def test_list_categories_empty_success(self):
        """
        Test listing categories when there are no categories.
        """

        Category.objects.all().delete()
        response = self.get_json(self.fragment)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["data"] == []

    def test_category_viewset_permissions(self):
        """
        Test that the CategoryViewSet allows any user to access the list of categories.
        """

        self.auth = None
        response = self.get_json(self.fragment)

        assert response.status_code == status.HTTP_200_OK
