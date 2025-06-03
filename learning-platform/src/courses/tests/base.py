import pytest
from courses.factories import CategoryFactory
from core.test import BaseAPITestCase


class BaseCourseModuleTestCase(BaseAPITestCase):
    @pytest.fixture(autouse=True)
    def setup(self, setup_fixtures):
        """
        Setup method to initialize the test case.
        """

        self.category_data = {
            "name": self.faker.sentence(nb_words=6),
            "description": self.faker.paragraph(nb_sentences=2),
        }

        self.fake_category = CategoryFactory(**self.category_data)
