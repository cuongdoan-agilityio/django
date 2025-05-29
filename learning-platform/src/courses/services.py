from courses.models import Course
from core.constants import Status
from core.error_messages import ErrorMessage


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

        if "status" in data and data["status"] == "inactive":
            if course.enrollments.exists():
                raise ValueError(ErrorMessage.COURSE_HAS_STUDENTS)

        for field, value in data.items():
            setattr(course, field, value)
        course.save()

        return course
