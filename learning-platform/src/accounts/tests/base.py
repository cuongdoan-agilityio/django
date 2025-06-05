import pytest
from django.contrib.auth import get_user_model
from django.db.models.signals import m2m_changed, post_save

from accounts.signals import send_verify_email
from accounts.factories import SpecializationFactory
from core.test import BaseAPITestCase
from courses.models import Course
from courses.signals import send_email_to_instructor

User = get_user_model()


class BaseAccountModuleTestCase(BaseAPITestCase):
    """
    Base test case for the accounts module, providing common setup and fixtures.
    """

    @pytest.fixture(autouse=True)
    def setup(self, setup_fixtures, db):
        """
        Setup method to initialize the test case.
        """

        post_save.disconnect(receiver=send_verify_email, sender=User)
        m2m_changed.disconnect(
            receiver=send_email_to_instructor, sender=Course.students.through
        )

        self.specialization_data = {
            "name": self.faker.sentence(nb_words=5),
            "description": self.faker.paragraph(nb_sentences=2),
        }

        self.fake_specialization = SpecializationFactory(**self.specialization_data)

        self.user_data = {
            "username": self.faker.user_name(),
            "email": self.faker.email(),
            "password": "Password@123",
            "first_name": self.faker.first_name(),
            "last_name": self.faker.last_name(),
            "phone_number": "0953625482",
            "date_of_birth": self.faker.date_between(
                start_date="-90y", end_date="-18y"
            ),
            "gender": self.random_gender,
        }

        self.student_data = {
            **self.user_data,
            "role": self.student_role,
            "scholarship": str(self.random_scholarship),
        }

        self.instructor_data = {
            **self.user_data,
            "username": self.faker.user_name(),
            "email": self.faker.email(),
            "role": self.instructor_role,
            "specializations": [str(self.fake_specialization.id)],
            "degree": self.random_degree,
        }
