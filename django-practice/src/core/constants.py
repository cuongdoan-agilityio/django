from enum import Enum


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
