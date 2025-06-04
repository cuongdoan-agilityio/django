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
