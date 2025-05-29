import pytest
from uuid import uuid4
from courses.services import CourseServices
from courses.models import Course
from core.constants import Status
from core.error_messages import ErrorMessage
from core.exceptions import CourseException, UserException, EnrollmentException


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

    def test_handle_partial_update_success(self, faker, fake_course):
        """
        Test that a course is successfully updated with valid data.
        """

        data = {
            "title": faker.sentence(nb_words=6),
            "description": faker.paragraph(nb_sentences=2),
        }
        updated_course = CourseServices().handle_partial_update(fake_course, data)

        assert updated_course.title == data["title"]
        assert updated_course.description == data["description"]
        assert updated_course.status == Status.ACTIVATE.value

    def test_handle_partial_update_inactive_course_with_students(self, math_enrollment):
        """
        Test that an exception is raised when trying to set a course to inactive while students are enrolled.
        """

        data = {"status": Status.INACTIVE.value}

        with pytest.raises(ValueError, match=ErrorMessage.COURSE_HAS_STUDENTS):
            CourseServices().handle_partial_update(math_enrollment.course, data)

    def test_handle_partial_update_change_status(self, fake_course):
        """
        Test that a course's status is successfully updated when no students are enrolled.
        """

        data = {"status": Status.INACTIVE.value}
        updated_course = CourseServices().handle_partial_update(fake_course, data)

        assert updated_course.status == Status.INACTIVE.value

    def test_handle_partial_update_no_changes(self, fake_course):
        """
        Test that the course remains unchanged when no valid fields are provided in the update data.
        """

        data = {}
        updated_course = CourseServices().handle_partial_update(fake_course, data)

        assert updated_course.title == fake_course.title

    def test_handle_enrollment_success(self, fake_student, fake_course):
        """
        Test that a student is successfully enrolled in a course.
        """

        CourseServices().handle_enrollment(user=fake_student, course=fake_course)

        assert fake_course.students.filter(id=fake_student.id).exists()

    def test_handle_enrollment_inactive_course(self, fake_student, fake_course):
        """
        Test that enrollment fails for inactive courses.
        """

        fake_course.status = Status.INACTIVE.value
        fake_course.save()

        with pytest.raises(CourseException) as exc_info:
            CourseServices().handle_enrollment(user=fake_student, course=fake_course)

        assert exc_info.value.code == "INACTIVE_COURSE"

    def test_handle_enrollment_course_full(
        self, fake_student, math_enrollment, math_enrollment_other, math_course
    ):
        """
        Test that enrollment fails when the course is full.
        """

        with pytest.raises(CourseException) as exc_info:
            CourseServices().handle_enrollment(user=fake_student, course=math_course)
        assert exc_info.value.code == "COURSE_IS_FULL"

    def test_handle_enrollment_invalid_student(
        self, fake_admin, authenticated_fake_admin, fake_course, fake_student
    ):
        """
        Test that enrollment fails for invalid student data.
        """

        with pytest.raises(UserException) as exc_info:
            CourseServices().handle_enrollment(
                user=fake_admin, course=fake_course, data={"student": str(uuid4())}
            )
        assert exc_info.value.code == "INVALID_USER_ID"

    def test_handle_enrollment_student_already_enrolled(
        self, math_course, math_enrollment, fake_student
    ):
        """
        Test that enrollment fails if the student is already enrolled.
        """

        with pytest.raises(EnrollmentException) as exc_info:
            CourseServices().handle_enrollment(user=fake_student, course=math_course)
        assert exc_info.value.code == "STUDENT_ALREADY_ENROLLED"

    def test_handle_leave_course_success(
        self,
        fake_student,
        fake_course,
        fake_enrollment,
    ):
        """
        Test that a student successfully leaves a course.
        """

        CourseServices().handle_leave_course(user=fake_student, course=fake_course)

        assert not fake_course.students.filter(id=fake_student.id).exists()

    def test_handle_leave_course_invalid_student(
        self,
        fake_admin,
        fake_course,
    ):
        """
        Test that leaving a course fails for invalid student data.
        """

        with pytest.raises(UserException) as exc_info:
            CourseServices().handle_leave_course(
                user=fake_admin, course=fake_course, data={"student": str(uuid4())}
            )
        assert exc_info.value.code == "INVALID_USER_ID"

    def test_handle_leave_course_student_not_enrolled(
        self,
        fake_student,
        fake_course,
    ):
        """
        Test that leaving a course fails if the student is not enrolled.
        """

        with pytest.raises(EnrollmentException) as exc_info:
            CourseServices().handle_leave_course(user=fake_student, course=fake_course)
        assert exc_info.value.code == "STUDENT_NOT_ENROLLED"

    def test_handle_leave_course_with_admin(
        self,
        fake_student,
        fake_admin,
        math_course,
        math_enrollment,
    ):
        """
        Test that a superuser can remove a student from a course.
        """

        CourseServices().handle_leave_course(
            user=fake_admin, course=math_course, data={"student": str(fake_student.id)}
        )

        assert not math_course.students.filter(id=fake_student.id).exists()
