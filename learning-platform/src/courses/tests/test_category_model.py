from django.test import TestCase
from django.core.exceptions import ValidationError
from faker import Faker
from courses.models import Category
from courses.factories import CategoryFactory


class CategoryModelTest(TestCase):
    """
    Test case for the Category model.
    """

    def setUp(self):
        """
        Set up the test case with a sample category.
        """

        fake = Faker()
        self.name = fake.sentence(nb_words=6)
        self.description = fake.paragraph(nb_sentences=2)
        self.category = CategoryFactory(name=self.name, description=self.description)

    def test_category_success(self):
        """
        Test created category successfully.
        """

        self.assertEqual(self.category.name, self.name)
        self.assertEqual(self.category.description, self.description)
        self.assertIsInstance(self.category, Category)

    def test_category_empty_name(self):
        """
        Test that a category cannot be created with an empty name.
        """

        with self.assertRaises(ValidationError):
            category = CategoryFactory(name="", description=self.description)
            category.full_clean()

    def test_category_str(self):
        """
        Test the string representation of the category.
        """

        self.assertEqual(str(self.category), self.name)

    def test_category_name_unique(self):
        """
        Test that the category name is unique.
        """

        with self.assertRaises(Exception):
            Category.objects.create(name=self.name)

    def test_category_help_text(self):
        """
        Test the help text for the category name field.
        """

        field_help_text = self.category._meta.get_field("name").help_text
        self.assertEqual(field_help_text, "Category name")
