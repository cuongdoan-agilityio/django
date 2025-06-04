from django.contrib.auth import get_user_model
from core.exceptions import UserException


User = get_user_model()


class UserServices:
    """
    A service class for handling user-related operations.
    """

    def update_user_profile(user, data):
        """
        Update the profile of a user.
        """

        if "scholarship" in data and not user.is_student:
            data.pop("scholarship")

        if "degree" in data and not user.is_instructor:
            data.pop("degree")

        if "specializations" in data and not user.is_instructor:
            data.pop("specializations")

        update_fields = []

        try:
            for field, value in data.items():
                if field == "specializations":
                    user.specializations.set(value)
                else:
                    setattr(user, field, value)
                    update_fields.append(field)
            user.save(update_fields=update_fields)
        except Exception:
            raise UserException(code="UPDATE_COURSE_FAILED")

        return user
