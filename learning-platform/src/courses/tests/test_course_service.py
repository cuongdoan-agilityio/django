import pytest
from uuid import uuid4

from courses.services import CourseServices
from courses.models import Course
from core.constants import Status
from core.exceptions import CourseException, UserException, EnrollmentException
from courses.factories import EnrollmentFactory

from .base import BaseCourseModuleTestCase


class TestCourseServices(BaseCourseModuleTestCase):
    """
    Unit tests for the CourseServices class.
    """

    def test_handle_create_course_success(self):
        """
        Test that a course is successfully created with valid data.
        """

        data = {
            "title": self.faker.sentence(nb_words=6),
            "category": self.fake_category,
            "description": self.faker.paragraph(nb_sentences=2),
            "status": Status.INACTIVE.value,
            "instructor": self.fake_instructor,
        }
        course = CourseServices().handle_create_course(data)

        assert course.title == data["title"]
        assert course.category == data["category"]
        assert course.description == data["description"]
        assert course.status == data["status"]
        assert course.instructor == self.fake_instructor
        assert Course.objects.filter(id=course.id).exists()

    def test_handle_create_course_missing_status(self):
        """
        Test that a course is created with default values when optional fields are missing.
        """

        data = {
            "title": self.faker.sentence(nb_words=6),
            "category": self.fake_category,
            "description": self.faker.paragraph(nb_sentences=2),
            "instructor": self.fake_instructor,
        }
        course = CourseServices().handle_create_course(data)

        assert course.title == data["title"]
        assert course.category == data["category"]
        assert course.description == data["description"]
        assert course.instructor == self.fake_instructor
        assert Course.objects.filter(id=course.id).exists()

        # Default status
        assert course.status == Status.ACTIVATE.value

    def test_handle_create_course_without_instructor(self):
        """
        Test handle create course without instructor.
        """

        data = {
            "title": self.faker.sentence(nb_words=6),
            "category": self.fake_category,
            "description": self.faker.paragraph(nb_sentences=2),
            "instructor": None,
        }

        course = CourseServices().handle_create_course(data)

        assert course.title == data["title"]
        assert course.category == data["category"]
        assert course.description == data["description"]
        assert course.status == Status.ACTIVATE.value
        assert course.instructor is None

    def test_handle_partial_update_success(self):
        """
        Test that a course is successfully updated with valid data.
        """

        data = {
            "title": self.faker.sentence(nb_words=6),
            "description": self.faker.paragraph(nb_sentences=2),
        }
        updated_course = CourseServices().handle_partial_update(self.fake_course, data)

        assert updated_course.title == data["title"]
        assert updated_course.description == data["description"]
        assert updated_course.status == Status.ACTIVATE.value

    def test_handle_partial_update_inactive_course_with_students(self):
        """
        Test that an exception is raised when trying to set a course to inactive while students are enrolled.
        """

        data = {"status": Status.INACTIVE.value}

        with pytest.raises(CourseException) as exc_info:
            CourseServices().handle_partial_update(self.math_enrollment.course, data)

        assert exc_info.value.code == "COURSE_HAS_STUDENTS"

    def test_handle_partial_update_change_status(self):
        """
        Test that a course's status is successfully updated when no students are enrolled.
        """

        data = {"status": Status.INACTIVE.value}
        updated_course = CourseServices().handle_partial_update(self.fake_course, data)

        assert updated_course.status == Status.INACTIVE.value

    def test_handle_partial_update_no_changes(self):
        """
        Test that the course remains unchanged when no valid fields are provided in the update data.
        """

        data = {}
        updated_course = CourseServices().handle_partial_update(self.fake_course, data)

        assert updated_course.title == self.fake_course.title

    def test_handle_enrollment_success(self):
        """
        Test that a student is successfully enrolled in a course.
        """

        CourseServices().handle_enrollment(
            user=self.fake_student, course=self.fake_course
        )

        assert self.fake_course.students.filter(id=self.fake_student.id).exists()

    def test_handle_enrollment_inactive_course(self):
        """
        Test that enrollment fails for inactive courses.
        """

        self.fake_course.status = Status.INACTIVE.value
        self.fake_course.save()

        with pytest.raises(CourseException) as exc_info:
            CourseServices().handle_enrollment(
                user=self.fake_student, course=self.fake_course
            )

        assert exc_info.value.code == "INACTIVE_COURSE"

    def test_handle_enrollment_course_full(self):
        """
        Test that enrollment fails when the course is full.
        """

        EnrollmentFactory(course=self.math_course, student=self.fake_other_student)
        with pytest.raises(CourseException) as exc_info:
            CourseServices().handle_enrollment(
                user=self.fake_student, course=self.math_course
            )
        assert exc_info.value.code == "COURSE_IS_FULL"

    def test_handle_enrollment_invalid_student(self):
        """
        Test that enrollment fails for invalid student data.
        """

        with pytest.raises(UserException) as exc_info:
            CourseServices().handle_enrollment(
                user=self.fake_admin,
                course=self.fake_course,
                data={"student": str(uuid4())},
            )
        assert exc_info.value.code == "INVALID_USER_ID"

    def test_handle_enrollment_student_already_enrolled(self):
        """
        Test that enrollment fails if the student is already enrolled.
        """

        self.music_course.students.add(self.fake_student)

        with pytest.raises(EnrollmentException) as exc_info:
            CourseServices().handle_enrollment(
                user=self.fake_student, course=self.music_course
            )
        assert exc_info.value.code == "STUDENT_ALREADY_ENROLLED"

    def test_handle_leave_course_success(self):
        """
        Test that a student successfully leaves a course.
        """

        self.fake_course.students.add(self.fake_student)
        CourseServices().handle_leave_course(
            user=self.fake_student, course=self.fake_course
        )

        assert not self.fake_course.students.filter(id=self.fake_student.id).exists()

    def test_handle_leave_course_invalid_student(self):
        """
        Test that leaving a course fails for invalid student data.
        """

        with pytest.raises(UserException) as exc_info:
            CourseServices().handle_leave_course(
                user=self.fake_admin,
                course=self.fake_course,
                data={"student": str(uuid4())},
            )
        assert exc_info.value.code == "INVALID_USER_ID"

    def test_handle_leave_course_student_not_enrolled(self):
        """
        Test that leaving a course fails if the student is not enrolled.
        """

        with pytest.raises(EnrollmentException) as exc_info:
            CourseServices().handle_leave_course(
                user=self.fake_student, course=self.fake_course
            )
        assert exc_info.value.code == "STUDENT_NOT_ENROLLED"

    def test_handle_leave_course_with_admin(self):
        """
        Test that a superuser can remove a student from a course.
        """

        CourseServices().handle_leave_course(
            user=self.fake_admin,
            course=self.math_course,
            data={"student": str(self.fake_student.id)},
        )

        assert not self.math_course.students.filter(id=self.fake_student.id).exists()

    def test_handle_get_students_of_course_success(self):
        """
        Test that students enrolled in a course are successfully retrieved.
        """

        EnrollmentFactory(course=self.math_course, student=self.fake_other_student)
        students = CourseServices().handle_get_students_of_course(
            course=self.math_course
        )

        assert len(students) == 2
        assert self.fake_other_student in students
        assert self.fake_student in students

    def test_handle_get_students_of_course_no_students(self):
        """
        Test that an empty list is returned when no students are enrolled in the course.
        """

        students = CourseServices().handle_get_students_of_course(
            course=self.fake_course
        )

        assert len(students) == 0
