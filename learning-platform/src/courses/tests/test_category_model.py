from django.core.exceptions import ValidationError
from courses.models import Category
from courses.factories import CategoryFactory
from core.tests.base import BaseTestCase


class CategoryModelTest(BaseTestCase):
    """
    Test case for the Category model.
    """

    def test_create_category_success(self):
        """
        Test created category successfully.
        """

        self.assertEqual(self.category.name, self.category_name)
        self.assertEqual(self.category.description, self.category_description)
        self.assertIsInstance(self.category, Category)

    def test_category_empty_name(self):
        """
        Test that a category cannot be created with an empty name.
        """

        with self.assertRaises(ValidationError):
            category = CategoryFactory(name="", description=self.category_description)
            category.full_clean()

    def test_category_str(self):
        """
        Test the string representation of the category.
        """

        self.assertEqual(str(self.category), self.category_name)

    def test_category_name_unique(self):
        """
        Test that the category name is unique.
        """

        with self.assertRaises(Exception):
            Category.objects.create(
                name=self.category_name,
                description=self.category_description,
            )

    def test_category_help_text(self):
        """
        Test the help text for the category name field.
        """

        field_help_text = self.category._meta.get_field("name").help_text
        self.assertEqual(field_help_text, "Category name")
