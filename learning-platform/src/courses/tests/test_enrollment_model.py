import pytest
from django.core.exceptions import ValidationError
from courses.models import Enrollment
from courses.factories import EnrollmentFactory
from .base import BaseCourseModuleTestCase


class TestEnrollmentModel(BaseCourseModuleTestCase):
    """
    Test case for the Enrollment model using pytest.
    """

    @pytest.fixture(autouse=True)
    def fake_enrollment_course(self, setup):
        """
        Fixture to create an Enrollment instance with a course and student.
        """

        self.fake_enrollment = EnrollmentFactory(
            course=self.fake_course, student=self.fake_student
        )

    def test_enrollment_success(self):
        """
        Test that an enrollment can be created successfully.
        """

        assert isinstance(self.fake_enrollment, Enrollment)

    def test_enrollment_course_relationship(self):
        """
        Test the relationship between Enrollment and Course.
        """

        assert self.fake_enrollment.course == self.fake_course

    def test_enrollment_student_relationship(self):
        """
        Test the relationship between Enrollment and Student.
        """

        assert self.fake_enrollment.student == self.fake_student

    def test_enrollment_without_course(self):
        """
        Test that an enrollment cannot be created with an invalid course.
        """

        with pytest.raises(ValidationError):
            invalid_enrollment = EnrollmentFactory.build(
                course=None, student=self.fake_student
            )
            invalid_enrollment.full_clean()

    def test_enrollment_without_student(self):
        """
        Test that an enrollment cannot be created with an invalid student.
        """

        with pytest.raises(ValidationError):
            invalid_enrollment = EnrollmentFactory.build(
                course=self.fake_course, student=None
            )
            invalid_enrollment.full_clean()
