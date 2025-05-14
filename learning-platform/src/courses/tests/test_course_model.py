import pytest
from django.core.exceptions import ValidationError
from courses.models import Course
from courses.factories import CourseFactory, CategoryFactory
from accounts.factories import UserFactory
from core.constants import Status


@pytest.mark.django_db
class TestCourseModel:
    """Test case for the Course model using pytest."""

    def test_course_success(self, fake_course, course_data):
        """
        Test that a course can be created successfully.
        """

        assert isinstance(fake_course, Course)
        assert fake_course.status in [status.value for status in Status]
        assert fake_course.title == course_data["title"]
        assert fake_course.description == course_data["description"]

    def test_course_str(self, fake_course, course_data):
        """
        Test the string representation of the course.
        """
        assert str(fake_course) == course_data["title"]

    def test_course_category_relationship(self, faker):
        """Test the relationship between Course and Category."""
        category_name = faker.sentence(nb_words=6)
        category_description = faker.paragraph(nb_sentences=3)
        category = CategoryFactory(name=category_name, description=category_description)
        course = CourseFactory(category=category)
        assert course.category.name == category_name
        assert course.category.description == category_description

    def test_course_instructor_relationship(self, faker):
        """Test the relationship between Course and Instructor."""
        username = faker.name()
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
        """Test that a course can be created with an empty description."""
        course = CourseFactory(description="")
        assert course.description == ""
        assert isinstance(course, Course)
