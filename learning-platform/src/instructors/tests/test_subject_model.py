from django.test import TestCase
from django.contrib.auth import get_user_model
from instructors.models import Subject
from instructors.factories import SubjectFactory


User = get_user_model()


class SubjectModelTest(TestCase):
    """
    Test case for the Subject model.
    """

    def setUp(self):
        """
        Set up the test case with a sample subject.
        """

        self.subject_name = "Mathematics"
        self.subject = SubjectFactory(name=self.subject_name)

    def test_subject_creation(self):
        """
        Test that a subject can be created successfully.
        """

        self.assertEqual(self.subject.name, self.subject_name)
        self.assertIsInstance(self.subject, Subject)

    def test_subject_str(self):
        """
        Test the string representation of the subject.
        """

        self.assertEqual(str(self.subject), self.subject_name)
