from rest_framework import status
from core.error_messages import ErrorMessage


class CourseErrorMessage:
    """
    Course error message.
    """

    COURSE_IS_FULL = ErrorMessage.COURSE_IS_FULL
    INACTIVE_COURSE = ErrorMessage.INACTIVE_COURSE


class UserErrorMessage:
    """
    User error message.
    """

    INVALID_USER_ID = ErrorMessage.INVALID_USER_ID


class EnrollmentErrorMessage:
    """
    Enrollment error message.
    """

    STUDENT_ALREADY_ENROLLED = ErrorMessage.STUDENT_ALREADY_ENROLLED
    STUDENT_NOT_ENROLLED = ErrorMessage.STUDENT_NOT_ENROLLED


class CustomBaseException(Exception):
    """
    Custom base exception.
    """

    default_code = ""
    error = None
    status_code = None

    def __init__(self, code=None, developer_message=None):
        self.developer_message = developer_message
        self.code = code if code is not None else self.default_code

        if not self.developer_message:
            self.developer_message = self.error

        if self.code and hasattr(self.error, code):
            self.developer_message = getattr(self.error, code)


class CourseException(CustomBaseException):
    """
    Course exception.
    """

    error = CourseErrorMessage
    status_code = status.HTTP_400_BAD_REQUEST


class UserException(CustomBaseException):
    """
    User exception.
    """

    error = UserErrorMessage
    default_code = "INVALID_USER_ID"
    status_code = status.HTTP_400_BAD_REQUEST


class EnrollmentException(CustomBaseException):
    """
    Enrollment exception.
    """

    error = EnrollmentErrorMessage
    default_code = "STUDENT_ALREADY_ENROLLED"
    status_code = status.HTTP_400_BAD_REQUEST
