import pytest
from courses.forms import EnrollmentForm
from core.constants import Status
from core.error_messages import ErrorMessage


@pytest.mark.django_db
class TestEnrollmentForm:
    """
    Test suite for the EnrollmentForm.
    """

    def test_valid_enrollment(self, fake_student, fake_course):
        """
        Test that the form is valid when the course is active, the student is valid, and the student is not already enrolled.
        """

        form_data = {"course": fake_course, "student": fake_student}
        form = EnrollmentForm(data=form_data)

        assert form.is_valid()

    def test_inactive_course(self, fake_course, fake_student):
        """
        Test that the form raises an error when the course is inactive.
        """

        fake_course.status = Status.INACTIVE.value
        fake_course.save()

        form_data = {"course": fake_course, "student": fake_student}
        form = EnrollmentForm(data=form_data)

        assert not form.is_valid()
        assert "course" in form.errors
        assert form.errors["course"] == [ErrorMessage.INACTIVE_COURSE]

    def test_invalid_student_role(self, fake_instructor, fake_course):
        """
        Test that the form raises an error when the user is not a student.
        """

        form_data = {"course": fake_course, "student": fake_instructor}
        form = EnrollmentForm(data=form_data)

        assert not form.is_valid()
        assert "student" in form.errors
        assert form.errors["student"] == [ErrorMessage.USER_NOT_STUDENT]

    def test_student_already_enrolled(self, fake_student, fake_course):
        """
        Test that the form raises an error when the student is already enrolled in the course.
        """

        fake_student.enrolled_courses.add(fake_course)
        form_data = {"course": fake_course, "student": fake_student}
        form = EnrollmentForm(data=form_data)

        assert not form.is_valid()
        assert "student" in form.errors
        assert form.errors["student"] == [ErrorMessage.STUDENT_ALREADY_ENROLLED]

    def test_missing_course_or_student(
        self,
        fake_student,
        fake_course,
    ):
        """
        Test that the form is invalid when either the course or student is missing.
        """

        form_data = {"student": fake_student}
        form = EnrollmentForm(data=form_data)

        assert not form.is_valid()

        form_data = {"course": fake_course}
        form = EnrollmentForm(data=form_data)

        assert not form.is_valid()
