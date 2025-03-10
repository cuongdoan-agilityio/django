from django.test import TestCase
from instructors.models import Instructor
from instructors.factories import InstructorFactory, SubjectFactory


class InstructorModelTest(TestCase):
    """
    Test case for the Instructor model.
    """

    def setUp(self):
        """
        Set up the test case with sample subjects and instructor.
        """

        self.math_subject = SubjectFactory(name="Mathematics")
        self.physics_subject = SubjectFactory(name="Physics")
        self.instructor = InstructorFactory(
            subjects=[self.math_subject, self.physics_subject]
        )

    def test_instructor_creation(self):
        """
        Test that an instructor can be created successfully.
        """

        self.assertIn(self.math_subject, self.instructor.subjects.all())
        self.assertIn(self.physics_subject, self.instructor.subjects.all())
        self.assertIsInstance(self.instructor, Instructor)

    def test_instructor_str(self):
        """
        Test the string representation of the instructor.
        """

        self.assertEqual(str(self.instructor), self.instructor.user.username)

    def test_instructor_get_subjects(self):
        """
        Test the get_subjects method of the instructor.
        """

        subjects = self.instructor.subjects.all()
        self.assertIn(self.math_subject, subjects)
        self.assertIn(self.physics_subject, subjects)
