import pytest
from courses.factories import CourseFactory, CategoryFactory
from django.contrib.auth import get_user_model
from django.db.models.signals import m2m_changed
from accounts.factories import UserFactory
from core.constants import Role, Status
from courses.factories import EnrollmentFactory
from courses.models import Course
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
def fake_enrollment(fake_course, fake_student):
    """
    Fixture to create an Enrollment instance with a course and student.
    """

    return EnrollmentFactory(course=fake_course, student=fake_student)


@pytest.fixture
def math_course(fake_instructor, disconnect_send_verify_email_signal):
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
def music_course(fake_instructor, disconnect_send_verify_email_signal):
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

    m2m_changed.connect(
        receiver=send_email_to_instructor, sender=Course.students.through
    )
    yield
    m2m_changed.disconnect(
        receiver=send_email_to_instructor, sender=Course.students.through
    )


@pytest.fixture
def category_url(root_url):
    """
    Fixture to provide the base URL for categories.
    """

    return f"{root_url}categories/"


@pytest.fixture
def fake_categories(db):
    """
    Fixture to create sample categories.
    """

    return [CategoryFactory(name="Programming"), CategoryFactory(name="Design")]


@pytest.fixture
def course_url(root_url):
    """
    Fixture to provide the base URL for courses.
    """

    return f"{root_url}courses/"


@pytest.fixture
def top_courses_url(root_url):
    """
    Fixture to provide the URL for fetching top courses.
    """

    return f"{root_url}courses/top/"


@pytest.fixture
def top_courses(db):
    """
    Fixture to create sample top courses.
    """

    return [
        CourseFactory(
            title="Python Programming",
            enrollment_count=50,
            status=Status.ACTIVATE.value,
        ),
        CourseFactory(
            title="Web Development", enrollment_count=30, status=Status.ACTIVATE.value
        ),
    ]


@pytest.fixture
def enroll_courses(math_course, music_course, db):
    """
    Create multiple courses for testing top-courses API.
    """

    math_course.enrollment_limit = music_course.enrollment_limit = 30
    math_course.save()
    music_course.save()

    EnrollmentFactory.create_batch(30, course=math_course)
    EnrollmentFactory.create_batch(20, course=music_course)
