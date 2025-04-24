from accounts.models import Specialization
from accounts.factories import SpecializationFactory
from core.tests.base import BaseTestCase


class SpecializationModelTest(BaseTestCase):
    """
    Test case for the Specialization model.
    """

    def setUp(self):
        """
        Set up the test case with a sample specialization.
        """
        super().setUp()

        self.name = self.fake.sentence(nb_words=5)
        self.description = self.fake.paragraph(nb_sentences=2)
        self.specialization = SpecializationFactory(
            name=self.name, description=self.description
        )

    def test_specialization_create_success(self):
        """
        Test that a specialization can be created successfully.
        """

        self.assertEqual(self.specialization.name, self.name)
        self.assertEqual(self.specialization.description, self.description)
        self.assertIsInstance(self.specialization, Specialization)

    def test_specialization_str(self):
        """
        Test the string representation of the specialization.
        """

        self.assertEqual(str(self.specialization), self.name)

    def test_specialization_update(self):
        """
        Test updating the name and description of a specialization.
        """

        new_name = self.fake.sentence(nb_words=5)
        new_description = self.fake.paragraph(nb_sentences=2)
        self.specialization.name = new_name
        self.specialization.description = new_description
        self.specialization.save()

        self.assertEqual(self.specialization.name, new_name)
        self.assertEqual(self.specialization.description, new_description)

    def test_specialization_delete(self):
        """
        Test that a specialization can be deleted successfully.
        """

        specialization_id = self.specialization.id
        self.specialization.delete()

        with self.assertRaises(Specialization.DoesNotExist):
            Specialization.objects.get(id=specialization_id)

    def test_specialization_unique_name(self):
        """
        Test that the specialization name must be unique.
        """

        with self.assertRaises(Exception):
            SpecializationFactory(name=self.name)
