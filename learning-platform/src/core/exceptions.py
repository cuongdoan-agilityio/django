class ErrorMessage:
    """
    All error messages
    """

    INVALID_CREDENTIALS = "Invalid credentials."
    INVALID_STUDENT_AGE = "Student age must be between 6 and 100 years."
    INVALID_INSTRUCTOR_AGE = "Instructor age must be between 18 and 100 years."
    SUBJECT_NOT_EXIST = "Subject does not exist."
    CATEGORY_NOT_EXIST = "Category does not exist."
    EMAIL_REQUIRED = "The Email must be set."
    PASSWORD_REQUIRED = "The Password must be set."
    PHONE_ONLY_NUMBER = "Phone numbers must contain numbers only."
    PASSWORD_LOWERCASE = "Password must contain at least one lowercase letter."
    PASSWORD_UPPERCASE = "Password must contain at least one uppercase letter."
    PASSWORD_NUMBER = "Password must contain at least one number."
    PASSWORD_SPECIAL_CHAR = "Password must contain at least one special character."
    EMAIL_EXISTS = "Email already exists. Please choose another one."
    USERNAME_EXISTS = "Username already exists. Please choose another one."
    PHONE_NUMBER_ONLY_NUMBER = "Phone numbers must contain numbers only."
    PHONE_NUMBER_INVALID_LENGTH = "Phone number must be 10 to 11 digits."
    INVALID_DATE_OF_BIRTH = "Invalid date of birth."
    STUDENT_ALREADY_ENROLLED = "This student is already enrolled in this course."
    STUDENT_NOT_ENROLLED = "You are not enrolled in this course."
    ALREADY_ENROLLED = "You are already enrolled in this course."
    COURSE_NOT_AVAILABLE = "This course is not available for enrollment."
    COURSE_HAS_STUDENTS = (
        "Cannot disable a course that is in progress and has students enrolled."
    )
