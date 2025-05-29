import pytest
from courses.services import CourseServices
from courses.models import Course
from core.constants import Status


@pytest.mark.django_db
class TestCourseServices:
    """
    Unit tests for the CourseServices class.
    """

    def test_handle_create_course_success(self, faker, fake_instructor, fake_category):
        """
        Test that a course is successfully created with valid data.
        """

        data = {
            "title": faker.sentence(nb_words=6),
            "category": fake_category,
            "description": faker.paragraph(nb_sentences=2),
            "status": Status.INACTIVE.value,
            "instructor": fake_instructor,
        }
        course = CourseServices().handle_create_course(data)

        assert course.title == data["title"]
        assert course.category == data["category"]
        assert course.description == data["description"]
        assert course.status == data["status"]
        assert course.instructor == fake_instructor
        assert Course.objects.filter(id=course.id).exists()

    def test_handle_create_course_missing_status(
        self, faker, fake_instructor, fake_category
    ):
        """
        Test that a course is created with default values when optional fields are missing.
        """

        data = {
            "title": faker.sentence(nb_words=6),
            "category": fake_category,
            "description": faker.paragraph(nb_sentences=2),
            "instructor": fake_instructor,
        }
        course = CourseServices().handle_create_course(data)

        assert course.title == data["title"]
        assert course.category == data["category"]
        assert course.description == data["description"]
        assert course.instructor == fake_instructor
        assert Course.objects.filter(id=course.id).exists()

        # Default status
        assert course.status == Status.ACTIVATE.value

    def test_handle_create_course_without_instructor(self, faker, fake_category):
        """
        Test handle create course without instructor.
        """

        data = {
            "title": faker.sentence(nb_words=6),
            "category": fake_category,
            "description": faker.paragraph(nb_sentences=2),
            "instructor": None,
        }

        course = CourseServices().handle_create_course(data)

        assert course.title == data["title"]
        assert course.category == data["category"]
        assert course.description == data["description"]
        assert course.status == Status.ACTIVATE.value
        assert course.instructor is None
