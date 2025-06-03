import pytest
from django.core.exceptions import ValidationError
from courses.models import Category
from courses.factories import CategoryFactory
from .base import BaseCourseModuleTestCase


class TestCategoryModel(BaseCourseModuleTestCase):
    """
    Test case for the Category model.
    """

    def test_create_category_success(self):
        """
        Test created category successfully.
        """
        assert self.fake_category.name == self.category_data.get("name")
        assert self.fake_category.description == self.category_data["description"]
        assert isinstance(self.fake_category, Category)

    def test_category_empty_name(self):
        """
        Test that a category cannot be created with an empty name.
        """

        with pytest.raises(ValidationError):
            category = CategoryFactory(
                name="", description=self.category_data["description"]
            )
            category.full_clean()

    def test_category_str(self):
        """
        Test the string representation of the category.
        """

        assert str(self.fake_category) == self.category_data["name"]

    def test_category_help_text(self):
        """
        Test the help text for the category name field.
        """

        field_help_text = self.fake_category._meta.get_field("name").help_text
        assert field_help_text == "Category name"
