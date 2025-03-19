from django.core.exceptions import ValidationError
from courses.models import Course
from courses.factories import CourseFactory, CategoryFactory
from instructors.factories import InstructorFactory
from core.constants import Status
from core.tests.base import BaseTestCase


class CourseModelTest(BaseTestCase):
    """
    Test case for the Course model.
    """

    def setUp(self):
        """
        Set up the test case with a sample course.
        """
        super().setUp()

        self.title = self.fake.sentence(nb_words=6)
        self.description = self.fake.paragraph(nb_sentences=3)
        self.course = CourseFactory(
            title=self.title,
            description=self.description,
        )

    def test_course_success(self):
        """
        Test that a course can be created successfully.
        """

        self.assertIsInstance(self.course, Course)
        self.assertIn(self.course.status, [status.value for status in Status])
        self.assertEqual(self.course.title, self.title)
        self.assertEqual(self.course.description, self.description)

    def test_course_str(self):
        """
        Test the string representation of the course.
        """

        self.assertEqual(str(self.course), self.title)

    def test_course_category_relationship(self):
        """
        Test the relationship between Course and Category.
        """

        category_name = self.fake.sentence(nb_words=6)
        category_description = self.fake.paragraph(nb_sentences=3)
        category = CategoryFactory(
            name=category_name,
            description=category_description,
        )
        course = CourseFactory(category=category)
        self.assertEqual(course.category.name, category_name)
        self.assertEqual(course.category.description, category_description)

    def test_course_instructor_relationship(self):
        """
        Test the relationship between Course and Instructor.
        """

        username = self.fake.name()
        instructor = InstructorFactory(user__username=username)
        course = CourseFactory(instructor=instructor)
        self.assertEqual(course.instructor.user.username, username)

    def test_course_empty_title(self):
        """
        Test that a course cannot be created with an empty title.
        """

        with self.assertRaises(ValidationError):
            course = CourseFactory.build(title="")
            course.full_clean()

    def test_course_empty_description(self):
        """
        Test that a course can be created with an empty description.
        """

        course = CourseFactory(description="")
        self.assertEqual(course.description, "")
        self.assertIsInstance(course, Course)
