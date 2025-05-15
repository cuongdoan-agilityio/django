import pytest
from courses.factories import CourseFactory, CategoryFactory
from django.db.models.signals import post_save
from django.contrib.auth import get_user_model
from accounts.factories import UserFactory
from core.constants import Role, Status
from courses.factories import EnrollmentFactory
from courses.models import Enrollment
from courses.signals import send_email_to_instructor


User = get_user_model()


@pytest.fixture
def share_data(faker):
    """
    Fixture to provide shared sample data for testing.
    """

    return {
        "password": "Password@123",
        "username": faker.user_name(),
        "first_name": faker.first_name(),
        "last_name": faker.last_name(),
        "email": faker.email(),
        "message": faker.sentence(),
        "is_read": faker.boolean(),
    }


@pytest.fixture
def course_data(faker):
    """
    Fixture to provide sample course data.
    Includes fields like title and description.
    """

    title = faker.sentence(nb_words=6)
    description = faker.paragraph(nb_sentences=3)
    return {"title": title, "description": description}


@pytest.fixture
def fake_course(course_data, disconnect_send_verify_email_signal, db):
    """
    Fixture to create a sample Course instance.
    Disconnects the `send_verify_email` signal to avoid side effects.
    """

    return CourseFactory(
        title=course_data["title"],
        description=course_data["description"],
        status=Status.ACTIVATE.value,
    )


@pytest.fixture
def category_data(faker):
    """
    Fixture to provide sample category data.
    Includes fields like name and description.
    """

    return {
        "name": faker.sentence(nb_words=6),
        "description": faker.paragraph(nb_sentences=2),
    }


@pytest.fixture
def fake_category(category_data):
    """
    Fixture to create a Category instance using the provided category data.
    """

    return CategoryFactory(**category_data)


@pytest.fixture
def fake_student(disconnect_send_verify_email_signal):
    """
    Fixture to create a sample student user.
    Disconnects the `send_verify_email` signal to avoid side effects.
    """

    return UserFactory(
        password="Password@123",
        role=Role.STUDENT.value,
    )


@pytest.fixture
def fake_enrollment(fake_course, fake_student):
    """
    Fixture to create an Enrollment instance with a course and student.
    """

    return EnrollmentFactory(course=fake_course, student=fake_student)


@pytest.fixture
def fake_instructor(disconnect_send_verify_email_signal):
    """
    Fixture to create a sample instructor user.
    Disconnects the `send_verify_email` signal to avoid side effects.
    """

    return UserFactory(role=Role.INSTRUCTOR.value)


@pytest.fixture
def math_course(fake_instructor):
    """
    Fixture to create a sample Math course with an instructor.
    """

    return CourseFactory(
        title="Math course",
        status=Status.ACTIVATE.value,
        enrollment_limit=2,
        instructor=fake_instructor,
    )


@pytest.fixture
def music_course(fake_instructor):
    """
    Fixture to create a sample Music course with an instructor.
    """

    return CourseFactory(
        title="Music Course",
        status=Status.ACTIVATE.value,
        instructor=fake_instructor,
    )


@pytest.fixture
def other_student_user(disconnect_send_verify_email_signal):
    """
    Fixture to create another sample student user.
    Disconnects the `send_verify_email` signal to avoid side effects.
    """

    return UserFactory(role=Role.STUDENT.value)


@pytest.fixture
def math_enrollment(math_course, fake_student):
    """
    Fixture to create an Enrollment instance for the Math course and a student.
    """

    return EnrollmentFactory(course=math_course, student=fake_student)


@pytest.fixture
def math_enrollment_other(math_course, other_student_user):
    """
    Fixture to fake math enrollment for other user.
    """

    return EnrollmentFactory(course=math_course, student=other_student_user)


@pytest.fixture
def music_enrollment(music_course, fake_student):
    """
    Fixture to create an Enrollment instance for the Music course and a student.
    """

    return EnrollmentFactory(course=music_course, student=fake_student)


@pytest.fixture
def connect_send_email_to_instructor_signal():
    """
    Fixture to connect the signal, and disconnect after the test
    """

    post_save.connect(receiver=send_email_to_instructor, sender=Enrollment)
    yield
    post_save.disconnect(receiver=send_email_to_instructor, sender=Enrollment)