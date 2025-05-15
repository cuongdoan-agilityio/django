import pytest
from accounts.models import Specialization
from accounts.factories import SpecializationFactory


@pytest.mark.django_db
class TestSpecializationModel:
    """
    Pytest class for the Specialization model tests.
    """

    def test_specialization_create_success(self, fake_specialization, specialization_data):
        """
        Test that a specialization can be created successfully.
        """

        assert fake_specialization.name == specialization_data["name"]
        assert fake_specialization.description == specialization_data["description"]
        assert isinstance(fake_specialization, Specialization)

    def test_specialization_str(self, fake_specialization, specialization_data):
        """
        Test the string representation of the specialization.
        """

        assert str(fake_specialization) == specialization_data["name"]

    def test_specialization_update(self, fake_specialization):
        """
        Test updating the name and description of a specialization.
        """
        new_name = "Updated Specialization Name"
        new_description = "Updated Description for Specialization"

        fake_specialization.name = new_name
        fake_specialization.description = new_description
        fake_specialization.save()

        assert fake_specialization.name == new_name
        assert fake_specialization.description == new_description

    def test_specialization_delete(self, fake_specialization):
        """
        Test that a specialization can be deleted successfully.
        """

        specialization_id = fake_specialization.id
        fake_specialization.delete()

        with pytest.raises(Specialization.DoesNotExist):
            Specialization.objects.get(id=specialization_id)

    def test_specialization_unique_name(self, specialization_data, fake_specialization):
        """
        Test that the specialization name must be unique.
        """

        with pytest.raises(Exception):
            SpecializationFactory(name=specialization_data["name"])
