from django.contrib.auth import get_user_model
from courses.models import Course
from core.constants import Status
from core.error_messages import ErrorMessage
from core.exceptions import CourseException, UserException, EnrollmentException
from notifications.models import Notification
from notifications.constants import NotificationMessage


User = get_user_model()


class CourseServices:
    """
    A service class for handling operations related to courses.
    """

    def handle_create_course(self, data):
        """
        Handles the creation of a new course.

        Args:
            data (dict): A dictionary containing the course details. Expected keys:
                - title (str): The title of the course.
                - category (str): The category of the course.
                - description (str): A brief description of the course.
                - status (str, optional): The status of the course (default is 'ACTIVATE').
                - instructor (User): The instructor associated with the course.

        Returns:
            Course: The created course instance.
        """

        course_data = {
            "title": data.get("title"),
            "category": data.get("category"),
            "description": data.get("description"),
            "status": data.get("status", Status.ACTIVATE.value),
            "instructor": data.get("instructor"),
        }

        course = Course.objects.create(**course_data)

        return course

    def handle_partial_update(self, course, data):
        """
        Handles partial updates to a course.

        Args:
            course (Course): The course instance to update.
            data (dict): The validated data for updating the course.

        Returns:
            Course: The updated course instance.

        Raises:
            ValueError: If the course cannot be updated due to business rules.
        """

        if "status" in data and data["status"] == Status.INACTIVE.value:
            if course.enrollments.exists():
                raise ValueError(ErrorMessage.COURSE_HAS_STUDENTS)

        for field, value in data.items():
            setattr(course, field, value)
        course.save()

        return course

    def handle_enrollment(self, user, course, data=None):
        """
        Handles the enrollment of a student in a course.

        Args:
            request (HttpRequest): The current request object.
            course (Course): The course instance.

        Returns:
            dict: A dictionary indicating the success of the enrollment.

        Raises:
            ValueError: If the student data is invalid or the user does not exist.
        """

        if course.status != Status.ACTIVATE.value:
            # Minh Tran: Must raise error at CourseException
            # Minh Tran: use is_staff
            # Khanh Nguyen: users/me/ should remove /me/
            # Khanh Nguyen: notification should user service such Use service to support notification to user device, such as Firebase Cloud Messaging
            raise CourseException(code="INACTIVE_COURSE")

        if course.is_full:
            raise CourseException(code="COURSE_IS_FULL")

        if user.is_superuser:
            try:
                student = User.objects.get(id=data["student"])
            except User.DoesNotExist:
                raise UserException(code="INVALID_USER_ID")
        else:
            student = user

        # Validate if the student is already enrolled
        if course.students.filter(id=student.id).exists():
            raise EnrollmentException(code="STUDENT_ALREADY_ENROLLED")

        # Add the student to the course
        course.students.add(student)

        # Create notification
        # TODO: Need refactor after implement Notification service
        Notification.objects.create(
            user=course.instructor,
            message=NotificationMessage.STUDENT_ENROLLED.format(
                user_name=student.username, course_name=course.title
            ),
        )

    def handle_leave_course(self, user, course, data=None):
        """
        Handles the logic for a student leaving a course.

        Args:
            user (User): The user attempting to leave the course.
            course (Course): The course instance.
            data (dict, optional): Additional data for leaving the course.

        Raises:
            UserException: If the student data is invalid or the user is not enrolled.
            CourseException: If the course is invalid or other business rules are violated.
        """

        # Determine the student based on the request
        if user.is_superuser:
            try:
                student = User.objects.get(id=data["student"])
            except User.DoesNotExist:
                raise UserException(code="INVALID_USER_ID")
        else:
            student = user

        # Validate if the student is enrolled in the course
        enrollment = student.enrollments.filter(course=course).first()
        if not enrollment:
            raise EnrollmentException(
                code="STUDENT_NOT_ENROLLED",
            )

        # Delete the enrollment
        enrollment.delete()

        # Create notification for the student
        # TODO: Need refactor after implement Notification service
        Notification.objects.create(
            user=student,
            message=NotificationMessage.STUDENT_UNENROLLED.format(
                course_name=course.title
            ),
        )

    def handle_get_students_of_course(self, course):
        """
        Handles the logic for retrieving students enrolled in a course.
        """

        students = User.objects.filter(enrollments__course=course).distinct()

        return students
