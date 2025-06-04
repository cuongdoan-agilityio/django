import pytest
from django.core.exceptions import ValidationError

from courses.forms import EnrollmentForm, EnrollmentInlineForm
from courses.factories import EnrollmentFactory
from core.constants import Status
from core.error_messages import ErrorMessage

from .base import BaseCourseModuleTestCase


class TestEnrollmentForm(BaseCourseModuleTestCase):
    """
    Test suite for the EnrollmentForm.
    """

    def test_valid_enrollment(self):
        """
        Test that the form is valid when the course is active, the student is valid, and the student is not already enrolled.
        """

        form_data = {"course": self.fake_course, "student": self.fake_student}
        form = EnrollmentForm(data=form_data)

        assert form.is_valid()

    def test_inactive_course(self):
        """
        Test that the form raises an error when the course is inactive.
        """

        self.fake_course.status = Status.INACTIVE.value
        self.fake_course.save()

        form_data = {"course": self.fake_course, "student": self.fake_student}
        form = EnrollmentForm(data=form_data)

        assert not form.is_valid()
        assert "course" in form.errors
        assert form.errors["course"] == [ErrorMessage.INACTIVE_COURSE]

    def test_invalid_student_role(self):
        """
        Test that the form raises an error when the user is not a student.
        """

        form_data = {"course": self.fake_course, "student": self.fake_instructor}
        form = EnrollmentForm(data=form_data)

        assert not form.is_valid()
        assert "student" in form.errors
        assert form.errors["student"] == [ErrorMessage.USER_NOT_STUDENT]

    def test_student_already_enrolled(self):
        """
        Test that the form raises an error when the student is already enrolled in the course.
        """

        self.fake_student.enrolled_courses.add(self.fake_course)
        form_data = {"course": self.fake_course, "student": self.fake_student}
        form = EnrollmentForm(data=form_data)

        assert not form.is_valid()
        assert "student" in form.errors
        assert form.errors["student"] == [ErrorMessage.STUDENT_ALREADY_ENROLLED]

    def test_missing_course_or_student(self):
        """
        Test that the form is invalid when either the course or student is missing.
        """

        form_data = {"student": self.fake_student}
        form = EnrollmentForm(data=form_data)

        assert not form.is_valid()

        form_data = {"course": self.fake_course}
        form = EnrollmentForm(data=form_data)

        assert not form.is_valid()


class TestEnrollmentInlineForm(BaseCourseModuleTestCase):
    """
    Test suite for the EnrollmentInlineForm.
    """

    def test_valid_enrollment(self):
        """
        Test that the form is valid when the course is active, the student is valid, and the student is not already enrolled.
        """

        form = EnrollmentInlineForm(
            data={"student": self.fake_student.id},
            instance=EnrollmentFactory(course=self.fake_course),
        )
        assert form.is_valid()

    def test_inactive_course(self):
        """
        Test that the form raises an error when the course is inactive.
        """

        self.fake_course.status = Status.INACTIVE.value
        self.fake_course.save()

        with pytest.raises(ValidationError) as err:
            EnrollmentInlineForm(
                data={"student": self.fake_student.id},
                instance=EnrollmentFactory(course=self.fake_course),
            )

        assert ErrorMessage.INACTIVE_COURSE in str(err.value)

    def test_student_already_enrolled(self):
        """
        Test that the form raises an error when the student is already enrolled in the course.
        """

        EnrollmentFactory(course=self.fake_course, student=self.fake_student)
        enrollment = EnrollmentFactory(course=self.fake_course)
        form = EnrollmentInlineForm(
            data={"student": self.fake_student.id}, instance=enrollment
        )

        with pytest.raises(ValidationError) as err:
            form.is_valid()
            form.clean()

        assert ErrorMessage.STUDENT_ALREADY_ENROLLED in str(err.value)

    def test_no_changes(self):
        """
        Test that the form does not raise validation errors if no changes are made.
        """

        enrollment = EnrollmentFactory(
            course=self.fake_course, student=self.fake_student
        )
        form = EnrollmentInlineForm(
            data={"student": self.fake_student.id}, instance=enrollment
        )

        assert form.is_valid()
