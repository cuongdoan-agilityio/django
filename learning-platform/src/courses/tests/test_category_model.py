from django.test import TestCase
from categories.models import Category
from categories.factories import CategoryFactory


class CategoryModelTest(TestCase):
    """
    Test case for the Category model.
    """

    def setUp(self):
        """
        Set up the test case with a sample category.
        """
        self.category_name = "Test Category"
        self.category = CategoryFactory(name=self.category_name)

    def test_category_creation(self):
        """
        Test created category successfully.
        """
        self.assertEqual(self.category.name, self.category_name)
        self.assertIsInstance(self.category, Category)

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
            Category.objects.create(name=self.category_name)

    def test_category_help_text(self):
        """
        Test the help text for the category name field.
        """
        field_help_text = self.category._meta.get_field("name").help_text
        self.assertEqual(field_help_text, "Category name")
