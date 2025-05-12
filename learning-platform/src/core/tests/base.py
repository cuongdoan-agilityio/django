import random
from faker import Faker
from rest_framework.test import APITestCase, APIClient
from rest_framework.authtoken.models import Token
from django.db.models.signals import post_save
from django.contrib.auth import get_user_model

from core.constants import Gender, ScholarshipChoices, Degree, Role
from accounts.factories import UserFactory, SpecializationFactory
from accounts.signals import send_verify_email, enroll_intro_course
from core.tests.utils.helpers import random_birthday, random_phone_number
from courses.factories import CategoryFactory
from courses.signals import send_email_to_instructor
from courses.models import Enrollment


fake = Faker()
User = get_user_model()


class BaseTestCase(APITestCase):
    def setUp(self):
        post_save.disconnect(receiver=send_verify_email, sender=User)
        post_save.disconnect(receiver=enroll_intro_course, sender=User)
        post_save.disconnect(receiver=send_email_to_instructor, sender=Enrollment)

        self.client = APIClient()
        self.fake = fake
        self.genders = [gender.value for gender in Gender]
        self.scholarships = [scholarship.value for scholarship in ScholarshipChoices]
        self.degrees = [degree.value for degree in Degree]
        self.root_url = "/api/v1/"
        self.password = "Password@123"

        self.username = fake.user_name()
        self.first_name = fake.first_name()
        self.last_name = fake.last_name()
        self.email = fake.email()
        self.student_role = Role.STUDENT.value
        self.instructor_role = Role.INSTRUCTOR.value
        self.admin_role = Role.ADMIN.value

        self.student_user = UserFactory(
            password=self.password,
            username=self.username,
            email=self.email,
            scholarship=random.choice(self.scholarships),
            role=Role.STUDENT.value,
        )

        self.user = self.student_user
        self.student_token = Token.objects.filter(user=self.student_user).first()

        self.instructor_email = fake.email()
        self.instructor_username = fake.user_name()
        self.specialization = SpecializationFactory(name=fake.sentence(nb_words=5))

        self.instructor_user = UserFactory(
            password=self.password,
            username=self.instructor_username,
            email=self.instructor_email,
            degree=random.choice(self.degrees),
            role=Role.INSTRUCTOR.value,
        )

        self.category_name = fake.sentence(nb_words=6)
        self.category_description = fake.paragraph(nb_sentences=2)
        self.category = CategoryFactory(
            name=self.category_name, description=self.category_description
        )

        self.student_token = Token.objects.create(user=self.student_user)
        self.instructor_token = Token.objects.create(user=self.instructor_user)

    def tearDown(self):
        post_save.connect(receiver=send_verify_email, sender=User)
        post_save.connect(receiver=enroll_intro_course, sender=User)

    def random_gender(self):
        """
        Random gender.
        """

        return random.choice(self.genders)

    def random_degree(self):
        """
        Random degree.
        """

        return random.choice(self.degrees)

    def random_scholarship(self):
        """
        Random scholarship.
        """

        return random.choice(self.scholarships)

    def random_date_of_birth(self, is_student=False):
        """
        Random date of birth.
        """

        return random_birthday(is_student=is_student)

    def random_user_phone_number(self):
        """
        Random phone number.
        """

        return random_phone_number()

    def authenticate_as_student(self):
        """
        Authenticate the test client as a student.
        """

        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.student_token.key}")

    def authenticate_as_instructor(self):
        """
        Authenticate the test client as an instructor.
        """

        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.instructor_token.key}")

    def get_json(self, url, email):
        """
        Perform a GET request with a token.
        """

        self.authenticate(email)
        return self.client.get(url, format="json")

    def patch_json(self, url, data, email):
        """
        Perform a PATCH request with a token.
        """

        self.authenticate(email)
        return self.client.patch(url, data, format="json")

    def post_json(self, url, data, email):
        """
        Perform a POST request with a token.
        """

        self.authenticate(email)
        return self.client.post(url, data)

    def put_json(self, url, data, email):
        """
        Perform a PUT request with a token.
        """

        self.authenticate(email)
        return self.client.put(url, data, format="json")

    def authenticate(self, email):
        """
        Authenticate the test client
        """

        if email == self.instructor_email:
            self.authenticate_as_instructor()
        else:
            self.authenticate_as_student()
