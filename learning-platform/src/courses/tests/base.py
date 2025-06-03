import pytest
from django.contrib.auth import get_user_model
from django.db.models.signals import m2m_changed, post_save

from accounts.signals import send_verify_email
from courses.models import Course
from courses.signals import send_email_to_instructor
from courses.factories import CourseFactory, CategoryFactory
from core.test import BaseAPITestCase
from core.constants import Status

User = get_user_model()


class BaseCourseModuleTestCase(BaseAPITestCase):
    @pytest.fixture(autouse=True)
    def setup(self, setup_fixtures, db):
        """
        Setup method to initialize the test case.
        """

        post_save.disconnect(receiver=send_verify_email, sender=User)
        m2m_changed.disconnect(
            receiver=send_email_to_instructor, sender=Course.students.through
        )

        self.category_data = {
            "name": self.faker.sentence(nb_words=6),
            "description": self.faker.paragraph(nb_sentences=2),
        }

        self.fake_category = CategoryFactory(**self.category_data)

        self.math_course = CourseFactory(
            title="Math course",
            status=Status.ACTIVATE.value,
            enrollment_limit=2,
            instructor=self.fake_instructor,
        )

        self.course_data = {
            "title": self.faker.sentence(nb_words=6),
            "description": self.faker.paragraph(nb_sentences=3),
        }

        self.fake_course = CourseFactory(
            title=self.course_data["title"],
            description=self.course_data["description"],
            status=Status.ACTIVATE.value,
        )

        self.math_course = CourseFactory(
            title="Math course",
            status=Status.ACTIVATE.value,
            enrollment_limit=2,
            instructor=self.fake_instructor,
        )
