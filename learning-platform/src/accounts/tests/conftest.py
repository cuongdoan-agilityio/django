import pytest
from faker import Faker

from accounts.factories import SpecializationFactory


fake = Faker()


@pytest.fixture
def specialization_data():
    """
    Fixture for creating specialization data.
    """

    name = fake.sentence(nb_words=5)
    description = fake.paragraph(nb_sentences=2)
    return {"name": name, "description": description}


@pytest.fixture
def fake_specialization(specialization_data):
    """
    Fixture for creating a specialization instance.
    """

    return SpecializationFactory(
        **specialization_data
    )
