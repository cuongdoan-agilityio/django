import pytest
from django.core.exceptions import ValidationError

from accounts.factories import UserFactory
from core.constants import Status
from courses.models import Course
from courses.factories import CourseFactory, CategoryFactory

from .base import BaseCourseModuleTestCase


class TestCourseModel(BaseCourseModuleTestCase):
    """Test case for the Course model using pytest."""

    def test_course_success(self):
        """
        Test that a course can be created successfully.
        """

        assert isinstance(self.fake_course, Course)
        assert self.fake_course.status in [status.value for status in Status]
        assert self.fake_course.title == self.course_data["title"]
        assert self.fake_course.description == self.course_data["description"]

    def test_course_str(self):
        """
        Test the string representation of the course.
        """

        assert str(self.fake_course) == self.course_data["title"]

    def test_course_category_relationship(self):
        """
        Test the relationship between Course and Category.
        """

        category_name = self.faker.sentence(nb_words=6)
        category_description = self.faker.paragraph(nb_sentences=3)
        category = CategoryFactory(name=category_name, description=category_description)
        course = CourseFactory(category=category)
        assert course.category.name == category_name
        assert course.category.description == category_description

    def test_course_instructor_relationship(self):
        """
        Test the relationship between Course and Instructor.
        """

        username = self.faker.name()
        instructor = UserFactory(username=username)
        course = CourseFactory(instructor=instructor)
        assert course.instructor.username == username

    def test_course_empty_title(self):
        """
        Test that a course cannot be created with an empty title.
        """

        with pytest.raises(ValidationError):
            course = CourseFactory.build(title="")
            course.full_clean()

    def test_course_empty_description(self):
        """
        Test that a course can be created with an empty description.
        """

        course = CourseFactory(description="")
        assert course.description == ""
        assert isinstance(course, Course)
