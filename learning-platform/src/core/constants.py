from enum import Enum


SPECIAL_CHARACTER_REGEX = r'[!-@#$%^&*()_+="]'


class BaseChoiceEnum(Enum):
    """
    The base class for choices enumeration.
    This enumeration is often uses with
    Django fields.
    """

    @classmethod
    def values(cls) -> list[int]:
        """
        Get values of enum.

        Returns:
            List[int]: List of values.
        """
        return [data.value for data in cls]

    @classmethod
    def choices(cls) -> list[tuple]:
        """
        Get choices of enum.

        Returns:
            List[Tuple]: List of choice.
        """
        return [(data.value, data.name) for data in cls]


class ScholarshipChoices(BaseChoiceEnum):
    """
    Scholarship choices enumeration.

    Attributes:
        ZERO (int): Zero scholarship.
        TWENTY_FIVE (int): 25% scholarship.
        FIFTY (int): 50% scholarship.
        SEVENTY_FIVE (int): 75% scholarship.
        FULL (int): 100% scholarship.
    """

    ZERO = 0
    TWENTY_FIVE = 25
    FIFTY = 50
    SEVENTY_FIVE = 75
    FULL = 100


class Gender(BaseChoiceEnum):
    """
    Gender class representing different genders for users.

    Attributes:
        MALE (str): Represents male gender.
        FEMALE (str): Represents female gender.
        OTHER (str): Represents other gender.
    """

    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class Degree(BaseChoiceEnum):
    """
    Degree class representing different academic degrees for users.

    Attributes:
        NO_DEGREE (str): Represents no degree.
        MASTER (str): Represents a bachelor's degree.
        MASTER (str): Represents a master's degree.
        DOCTORATE (str): Represents a doctorate degree.
    """

    NO = "no"
    BACHELOR = "bachelor"
    MASTER = "master"
    DOCTORATE = "doctorate"


class Status(BaseChoiceEnum):
    """
    Status class representing different status.

    Attributes:
        ACTIVATE (str): Represents activate.
        INACTIVE (str): Represents inactive.
    """

    ACTIVATE = "activate"
    INACTIVE = "inactive"


class Role(BaseChoiceEnum):
    """
    Role class representing different roles for users.
    Attributes:
        STUDENT (str): Represents student role.
        INSTRUCTOR (str): Represents instructor role.
        ADMIN (str): Represents admin role.
    """

    STUDENT = "student"
    INSTRUCTOR = "instructor"
    ADMIN = "admin"
