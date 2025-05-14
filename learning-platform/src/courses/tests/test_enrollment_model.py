import pytest
from django.core.exceptions import ValidationError
from courses.models import Enrollment
from courses.factories import EnrollmentFactory


@pytest.mark.django_db
class TestEnrollmentModel:
    """
    Test case for the Enrollment model using pytest.
    """

    def test_enrollment_success(self, fake_enrollment):
        """
        Test that an enrollment can be created successfully.
        """
        assert isinstance(fake_enrollment, Enrollment)

    def test_enrollment_course_relationship(self, fake_enrollment, fake_course):
        """
        Test the relationship between Enrollment and Course.
        """
        assert fake_enrollment.course == fake_course

    def test_enrollment_student_relationship(self, fake_enrollment, fake_student):
        """
        Test the relationship between Enrollment and Student.
        """
        assert fake_enrollment.student == fake_student

    def test_enrollment_without_course(self, fake_student):
        """
        Test that an enrollment cannot be created with an invalid course.
        """
        with pytest.raises(ValidationError):
            invalid_enrollment = EnrollmentFactory.build(course=None, student=fake_student)
            invalid_enrollment.full_clean()

    def test_enrollment_without_student(self, fake_course):
        """
        Test that an enrollment cannot be created with an invalid student.
        """
        with pytest.raises(ValidationError):
            invalid_enrollment = EnrollmentFactory.build(course=fake_course, student=None)
            invalid_enrollment.full_clean()
