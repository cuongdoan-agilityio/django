from accounts.services import UserServices
from .base import BaseAccountModuleTestCase


class TestUpdateUserProfile(BaseAccountModuleTestCase):
    """
    Unit tests for the update_user_profile method in UserServices.
    """

    def test_update_user_profile_success(self):
        """
        Test that a user's profile is successfully updated.
        """

        data = {
            "first_name": self.faker.first_name(),
            "last_name": self.faker.last_name(),
            "scholarship": self.random_scholarship,
        }

        updated_user = UserServices().update_user_profile(self.fake_other_student, data)

        assert updated_user.first_name == data.get("first_name")
        assert updated_user.last_name == data.get("last_name")
        assert updated_user.scholarship == data.get("scholarship")

    def test_update_user_profile_invalid_field(self):
        """
        Test that invalid fields are ignored during the update.
        """

        data = {
            "non_existent_field": "Invalid",
            "first_name": self.faker.first_name(),
        }

        updated_user = UserServices().update_user_profile(self.fake_other_student, data)

        assert updated_user.first_name == data.get("first_name")
        assert not hasattr(updated_user, "non_existent_field")

    def test_update_user_profile_restricted_field_for_student(self):
        """
        Test that restricted fields for students are ignored.
        """

        data = {
            "degree": self.random_degree,
            "scholarship": self.random_scholarship,
        }

        updated_user = UserServices().update_user_profile(self.fake_other_student, data)

        assert updated_user.scholarship == data.get("scholarship")
        assert not hasattr(updated_user, "degree")

    def test_update_user_profile_restricted_field_for_instructor(self):
        """
        Test that restricted fields for instructors are ignored.
        """

        data = {
            "degree": self.random_degree,
            "scholarship": self.random_scholarship,
        }

        updated_user = UserServices().update_user_profile(self.fake_other_student, data)

        assert updated_user.degree == data.get("degree")
        assert not hasattr(updated_user, "scholarship")

    def test_update_user_profile_specializations(self):
        """
        Test that specializations are updated correctly for instructors.
        """

        data = {
            "specializations": [str(self.fake_specialization.id)],
        }

        updated_user = UserServices().update_user_profile(self.fake_instructor, data)

        assert updated_user.specializations.count() == 1
        assert (
            self.fake_specialization.name
            in updated_user.specializations.values_list("name", flat=True)
        )
