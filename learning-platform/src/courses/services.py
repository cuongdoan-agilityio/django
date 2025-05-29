from courses.models import Course
from core.constants import Status


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
