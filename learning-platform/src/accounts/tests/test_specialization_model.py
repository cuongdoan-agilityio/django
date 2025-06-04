import pytest
from accounts.models import Specialization
from accounts.factories import SpecializationFactory
from .base import BaseAccountModuleTestCase


class TestSpecializationModel(BaseAccountModuleTestCase):
    """
    Pytest class for the Specialization model tests.
    """

    def test_specialization_create_success(self):
        """
        Test that a specialization can be created successfully.
        """

        assert self.fake_specialization.name == self.specialization_data["name"]
        assert (
            self.fake_specialization.description
            == self.specialization_data["description"]
        )
        assert isinstance(self.fake_specialization, Specialization)

    def test_specialization_str(self):
        """
        Test the string representation of the specialization.
        """

        assert str(self.fake_specialization) == self.specialization_data["name"]

    def test_specialization_update(self):
        """
        Test updating the name and description of a specialization.
        """
        new_name = "Updated Specialization Name"
        new_description = "Updated Description for Specialization"

        self.fake_specialization.name = new_name
        self.fake_specialization.description = new_description
        self.fake_specialization.save()

        assert self.fake_specialization.name == new_name
        assert self.fake_specialization.description == new_description

    def test_specialization_delete(self):
        """
        Test that a specialization can be deleted successfully.
        """

        specialization_id = self.fake_specialization.id
        self.fake_specialization.delete()

        with pytest.raises(Specialization.DoesNotExist):
            Specialization.objects.get(id=specialization_id)

    def test_specialization_unique_name(self):
        """
        Test that the specialization name must be unique.
        """

        with pytest.raises(Exception):
            SpecializationFactory(name=self.specialization_data["name"])
