import pytest
import random
from uuid import uuid4
from faker import Faker
from django.db.models.signals import post_save
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token

from accounts.signals import send_verify_email, enroll_intro_course
from core.constants import Degree, Gender, ScholarshipChoices, Role
from accounts.factories import UserFactory


User = get_user_model()


@pytest.fixture(autouse=True)
def disconnect_send_verify_email_signal():
    """
    Fixture to disconnect the signal.
    """

    post_save.disconnect(receiver=send_verify_email, sender=User)


@pytest.fixture(scope="session")
def random_gender():
    """
    Fixture for random gender data.
    """

    genders = [gender.value for gender in Gender]
    return random.choice(genders)


@pytest.fixture
def random_scholarship():
    """
    Fixture for random scholarship.
    """

    scholarships = [choice.value for choice in ScholarshipChoices]
    return random.choice(scholarships)


@pytest.fixture(scope="session")
def random_degree():
    """
    Fixture for random degree.
    """

    degrees = [choice.value for choice in Degree]
    return random.choice(degrees)


@pytest.fixture
def send_verify_email_signal():
    """
    Fixture to connect the `send_verify_email` signal for the User model.
    Disconnects the signal after the test to avoid side effects.
    """

    post_save.connect(receiver=send_verify_email, sender=User)
    yield
    post_save.disconnect(receiver=send_verify_email, sender=User)


@pytest.fixture
def enroll_intro_course_signal():
    """
    Fixture to connect the `enroll_intro_course` signal for the User model.
    Disconnects the signal after the test to avoid side effects.
    """

    post_save.connect(receiver=enroll_intro_course, sender=User)
    yield
    post_save.disconnect(receiver=enroll_intro_course, sender=User)


@pytest.fixture()
def share_user_data(faker, random_degree):
    """
    Fixture to provide an user data include student and instructor.
    """

    password = "Password@123"

    return {
        "student": {
            "password": password,
            "username": faker.user_name(),
            "first_name": faker.first_name(),
            "last_name": faker.last_name(),
            "email": faker.email(),
        },
        "other_student": {
            "password": password,
            "username": faker.user_name(),
            "first_name": faker.first_name(),
            "last_name": faker.last_name(),
            "email": faker.email(),
        },
        "instructor": {
            "password": password,
            "username": faker.user_name(),
            "first_name": faker.first_name(),
            "last_name": faker.last_name(),
            "email": faker.email(),
            "degree": random_degree,
        },
    }


@pytest.fixture()
def fake_student(faker, share_user_data):
    """
    Fixture to create a sample student user instance.
    """

    post_save.disconnect(receiver=send_verify_email, sender=User)
    data = share_user_data.get("student")

    return UserFactory(
        password=data.get("password"),
        username=data.get("username"),
        email=data.get("email"),
        role=Role.STUDENT.value,
    )


@pytest.fixture()
def fake_student_token(fake_student):
    """
    Fixture to create a authentication token for student user.
    """

    return Token.objects.create(user=fake_student)


@pytest.fixture()
def fake_instructor(faker, share_user_data):
    """
    Fixture to create instructor user.
    """

    post_save.disconnect(receiver=send_verify_email, sender=User)
    data = share_user_data.get("instructor")

    return UserFactory(
        username=data.get("username"),
        password=data.get("password"),
        email=data.get("email"),
        role=Role.INSTRUCTOR.value,
    )


@pytest.fixture
def fake_other_student(faker, share_user_data):
    """
    Fixture to create a sample student user instance.
    """

    post_save.disconnect(receiver=send_verify_email, sender=User)
    data = share_user_data.get("other_student")

    return UserFactory(
        password=data.get("password"),
        username=data.get("username"),
        email=data.get("email"),
        role=Role.STUDENT.value,
    )


@pytest.fixture()
def fake_admin(faker):
    """
    Fixture to create instructor user.
    """

    post_save.disconnect(receiver=send_verify_email, sender=User)

    return UserFactory(
        username=faker.user_name(),
        password="Password@123",
        email=faker.email(),
        role=Role.ADMIN.value,
        is_staff=True,
        is_superuser=True,
    )


@pytest.fixture
def fake_instructor_token(fake_instructor):
    """
    Fixture to create and return a token for the instructor user.
    """

    return Token.objects.create(user=fake_instructor)


@pytest.fixture
def fake_admin_token(fake_admin):
    """
    Fixture to create and return a token for the instructor user.
    """

    return Token.objects.create(user=fake_admin)


@pytest.fixture()
def authenticated_fake_student(api_client, fake_student_token):
    """
    Fixture to authenticate student user.
    """

    api_client.credentials(HTTP_AUTHORIZATION=f"Token {fake_student_token.key}")

    yield api_client

    api_client.logout()


@pytest.fixture()
def authenticated_fake_instructor(api_client, fake_instructor_token):
    """
    Fixture to authenticate instructor user.
    """

    api_client.credentials(HTTP_AUTHORIZATION=f"Token {fake_instructor_token.key}")

    yield api_client

    api_client.logout()


@pytest.fixture()
def authenticated_fake_admin(api_client, fake_admin_token):
    """
    Fixture to authenticate instructor user.
    """

    api_client.credentials(HTTP_AUTHORIZATION=f"Token {fake_admin_token.key}")

    yield api_client

    api_client.logout()


@pytest.mark.django_db
class BaseAPITestCase:
    @pytest.fixture(autouse=True)
    def setup_fixtures(
        self,
        disconnect_send_verify_email_signal,
        random_gender,
        random_scholarship,
        random_degree,
        send_verify_email_signal,
        enroll_intro_course_signal,
        share_user_data,
        fake_student,
        fake_student_token,
        fake_instructor,
        fake_other_student,
        fake_admin,
        fake_instructor_token,
        fake_admin_token,
        authenticated_fake_student,
        authenticated_fake_instructor,
        authenticated_fake_admin,
    ):
        self.faker = Faker()
        self.root_url = "/api/v1/"
        self.disconnect_send_verify_email_signal = disconnect_send_verify_email_signal
        self.random_gender = random_gender
        self.student_role = Role.STUDENT.value
        self.instructor_role = Role.INSTRUCTOR.value
        self.admin_role = Role.ADMIN.value
        self.random_scholarship = random_scholarship
        self.random_degree = random_degree
        self.send_verify_email_signal = send_verify_email_signal
        self.enroll_intro_course_signal = enroll_intro_course_signal
        self.api_client = APIClient()
        self.share_user_data = share_user_data
        self.fake_student = fake_student
        self.fake_student_token = fake_student_token
        self.fake_instructor = fake_instructor
        self.fake_other_student = fake_other_student
        self.fake_admin = fake_admin
        self.fake_instructor_token = fake_instructor_token
        self.fake_admin_token = fake_admin_token
        self.authenticated_fake_student = authenticated_fake_student
        self.authenticated_fake_instructor = authenticated_fake_instructor
        self.authenticated_fake_admin = authenticated_fake_admin
        self.authenticated_token = self.fake_student_token
        self.auth = "token"

    def build_api_url(self, fragment: str = None) -> str:
        """
        Build the API URL.
        """

        uri = self.root_url

        if fragment:
            uri = f"{uri}{fragment}"

        return uri

    def get_json(self, fragment=None, data_format="json", **params):
        """
        Send a GET request to the API and return the response.

        Args:
            fragment (str, optional): The fragment of the URL to be appended to the base URL. Defaults to "".
            data_format (str, optional): The format of the data to be sent with the request.
            params (dict, optional): The parameters to be sent with the request.

        Returns:
            Response: Response data
        """

        url = self.build_api_url(fragment)

        headers = {}

        if self.auth == "token":
            headers["HTTP_AUTHORIZATION"] = f"Token {self.authenticated_token.key}"
        elif self.auth == "invalid_auth_token":
            invalid_token = str(uuid4())
            headers["HTTP_AUTHORIZATION"] = f"Token {invalid_token}"
        else:
            headers["HTTP_AUTHORIZATION"] = None

        self.api_client.credentials(**headers)

        return (
            self.api_client.get(url, format=data_format)
            if data_format
            else self.api_client.get(url)
        )

    def post_json(self, fragment, data, **params):
        """
        Send a POST request to the API.

        Args:
            fragment (str, optional): The fragment of the URL to be appended to the base URL. Defaults to "".
            data (dict, optional): The data to be sent with the request. Defaults to None.
            params (dict, optional): The parameters to be sent with the request.

        Returns:
            Response: Response data
        """

        url = self.build_api_url(fragment)

        headers = {}

        if self.auth == "token":
            headers["HTTP_AUTHORIZATION"] = f"Token {self.authenticated_token.key}"
        elif self.auth == "invalid_auth_token":
            invalid_token = str(uuid4())
            headers["HTTP_AUTHORIZATION"] = f"Token {invalid_token}"
        else:
            headers["HTTP_AUTHORIZATION"] = None

        self.api_client.credentials(**headers)

        return self.api_client.post(url, format="json", data=data)

    def patch_json(self, fragment="", data=None, **params):
        """
        Send a PATCH request to the API.

        Args:
            fragment: The fragment of the URL to be appended to the base URL.
            data: The data to be sent with the request.
            params: The parameters to be sent with the request.
        """
        url = self.build_api_url(fragment)

        headers = {}

        if self.auth == "token":
            headers["HTTP_AUTHORIZATION"] = f"Token {self.authenticated_token.key}"
        elif self.auth == "invalid_auth_token":
            invalid_token = str(uuid4())
            headers["HTTP_AUTHORIZATION"] = f"Token {invalid_token}"
        else:
            headers["HTTP_AUTHORIZATION"] = None

        self.api_client.credentials(**headers)

        return self.api_client.patch(url, format="json", data=data)

    def put_json(self, fragment="", data=None, **params):
        """
        Send a PUT request to the API.

        This is a convenience method for the common case of sending a PUT request.
        This method is used when the user is authenticated and has the correct permissions.

        Args:
            fragment (str, optional): The fragment of the URL to be appended to the base URL. Defaults to "".
            data (dict, optional): The data to be sent with the request. Defaults to None.
            params (dict, optional): The parameters to be sent with the request.

        Returns:
            Response: Response data
        """
        url = self.build_api_url(fragment)

        headers = {}

        if self.auth == "token":
            headers["HTTP_AUTHORIZATION"] = f"Token {self.authenticated_token.key}"
        elif self.auth == "invalid_auth_token":
            invalid_token = str(uuid4())
            headers["HTTP_AUTHORIZATION"] = f"Token {invalid_token}"
        else:
            headers["HTTP_AUTHORIZATION"] = None

        self.api_client.credentials(**headers)

        return self.api_client.put(url, format="json", data=data)
