import pytest
from django.core.exceptions import ValidationError
from courses.models import Category
from courses.factories import CategoryFactory


@pytest.mark.django_db
class TestCategoryModel:
    """
    Test case for the Category model.
    """

    def test_create_category_success(self, category_data, fake_category):
        """
        Test created category successfully.
        """
        assert fake_category.name == category_data.get("name")
        assert fake_category.description == category_data["description"]
        assert isinstance(fake_category, Category)

    def test_category_empty_name(self, category_data):
        """
        Test that a category cannot be created with an empty name.
        """

        with pytest.raises(ValidationError):
            category = CategoryFactory(
                name="", description=category_data["description"]
            )
            category.full_clean()

    def test_category_str(self, fake_category, category_data):
        """
        Test the string representation of the category.
        """

        assert str(fake_category) == category_data["name"]

    def test_category_name_unique(self, category_data):
        """
        Test that the category name is unique.
        """

        CategoryFactory(**category_data)
        with pytest.raises(Exception):
            Category.objects.create(**category_data)

    def test_category_help_text(self, fake_category):
        """
        Test the help text for the category name field.
        """

        field_help_text = fake_category._meta.get_field("name").help_text
        assert field_help_text == "Category name"
