from django.test import TestCase
from courses.models import Course
from courses.factories import CourseFactory
from categories.factories import CategoryFactory
from instructors.factories import InstructorFactory
from core.constants import Status


class CourseModelTest(TestCase):
    """
    Test case for the Course model.
    """

    def setUp(self):
        """
        Set up the test case with a sample course.
        """

        self.title = "Math"
        self.course = CourseFactory(
            title=self.title,
        )

    def test_course_creation(self):
        """
        Test that a course can be created successfully.
        """

        self.assertIsInstance(self.course, Course)
        self.assertIn(self.course.status, [status.value for status in Status])

    def test_course_str(self):
        """
        Test the string representation of the course.
        """

        self.assertEqual(str(self.course), self.title)

    def test_course_category_relationship(self):
        """
        Test the relationship between Course and Category.
        """

        name = "Science"
        category = CategoryFactory(name=name)
        course = CourseFactory(category=category)
        self.assertEqual(course.category.name, name)

    def test_course_instructor_relationship(self):
        """
        Test the relationship between Course and Instructor.
        """

        username = "instructor"
        instructor = InstructorFactory(user__username=username)
        course = CourseFactory(instructor=instructor)
        self.assertEqual(course.instructor.user.username, username)
