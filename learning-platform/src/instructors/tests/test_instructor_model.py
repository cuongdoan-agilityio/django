import random
from django.contrib.auth import get_user_model

from instructors.models import Instructor
from instructors.factories import InstructorFactory, SubjectFactory
from core.constants import Degree
from accounts.factories import UserFactory

from core.tests.base import BaseTestCase


User = get_user_model()


class InstructorModelTest(BaseTestCase):
    """
    Test case for the Instructor model.
    """

    def setUp(self):
        """
        Set up the test case with sample subjects and instructor.
        """
        super().setUp()

        self.gender = self.random_gender()
        self.email = self.fake.email()
        self.username = self.fake.user_name()
        self.math_subject = SubjectFactory(name="Mathematics")
        self.physics_subject = SubjectFactory(name="Physics")

        self.user = UserFactory(
            username=self.username,
            email=self.email,
            gender=self.gender,
        )
        self.instructor = InstructorFactory(
            user=self.user, subjects=[self.math_subject, self.physics_subject]
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

    def test_instructor_gender(self):
        """
        Test that the gender field is correctly set.
        """

        self.assertEqual(self.instructor.user.gender, self.gender)

    def test_instructor_email(self):
        """
        Test that the email field is correctly set.
        """

        self.assertEqual(self.instructor.user.email, self.email)

    def test_instructor_update_degree(self):
        """
        Test updating the degree field of a instructor.
        """

        degree = random.choice([degree.value for degree in Degree])
        self.instructor.degree = degree
        self.instructor.save()
        self.assertEqual(self.instructor.degree, degree)

    def test_delete_instructor(self):
        """
        Test that deleting a instructor does not delete the associated user.
        """

        self.instructor.delete()
        self.assertTrue(User.objects.filter(username=self.username).exists())
        self.assertFalse(Instructor.objects.filter(user=self.user).exists())
