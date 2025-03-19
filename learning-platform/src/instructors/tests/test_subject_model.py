from instructors.models import Subject
from instructors.factories import SubjectFactory
from core.tests.base import BaseTestCase


class SubjectModelTest(BaseTestCase):
    """
    Test case for the Subject model.
    """

    def setUp(self):
        """
        Set up the test case with a sample subject.
        """
        super().setUp()

        self.name = self.fake.sentence(nb_words=5)
        self.description = self.fake.paragraph(nb_sentences=2)
        self.subject = SubjectFactory(name=self.name, description=self.description)

    def test_subject_create_success(self):
        """
        Test that a subject can be created successfully.
        """

        self.assertEqual(self.subject.name, self.name)
        self.assertEqual(self.subject.description, self.description)
        self.assertIsInstance(self.subject, Subject)

    def test_subject_str(self):
        """
        Test the string representation of the subject.
        """

        self.assertEqual(str(self.subject), self.name)

    def test_subject_update(self):
        """
        Test updating the name and description of a subject.
        """

        new_name = self.fake.sentence(nb_words=5)
        new_description = self.fake.paragraph(nb_sentences=2)
        self.subject.name = new_name
        self.subject.description = new_description
        self.subject.save()

        self.assertEqual(self.subject.name, new_name)
        self.assertEqual(self.subject.description, new_description)

    def test_subject_delete(self):
        """
        Test that a subject can be deleted successfully.
        """

        subject_id = self.subject.uuid
        self.subject.delete()

        with self.assertRaises(Subject.DoesNotExist):
            Subject.objects.get(uuid=subject_id)

    def test_subject_unique_name(self):
        """
        Test that the subject name must be unique.
        """

        with self.assertRaises(Exception):
            SubjectFactory(name=self.name)
