from rest_framework import status
from rest_framework.test import APITestCase

from accounts.factories import UserFactory
from categories.factories import CategoryFactory
from core.constants import Status
from courses.factories import CourseFactory
from students.factories import StudentFactory
from enrollments.models import Enrollment
from instructors.factories import InstructorFactory


class CourseViewSetTest(APITestCase):
    """
    Test case for the CourseViewSet.
    """

    def setUp(self):
        """
        Set up the test case with sample data.
        """

        self.instructor_email = "instructor@example.com"
        self.instructor_username = "instructor"
        self.student_email = "student@example.com"
        self.student_username = "student"
        self.password = "Password@1234"

        self.instructor_user = UserFactory(
            username=self.instructor_username,
            email=self.instructor_email,
            password=self.password,
        )
        self.student_user = UserFactory(
            username=self.student_username,
            email=self.student_email,
            password=self.password,
        )

        self.category = CategoryFactory()
        self.student = StudentFactory(user=self.student_user)
        self.instructor = InstructorFactory(user=self.instructor_user)
        self.course = CourseFactory(
            title="Test Course",
            instructor=self.instructor,
            status=Status.ACTIVATE.value,
        )

        self.url_list = "/api/v1/courses/"
        self.url_detail = f"/api/v1/courses/{self.course.uuid}/"
        self.url_enroll = f"/api/v1/courses/{self.course.uuid}/enroll/"
        self.url_leave = f"/api/v1/courses/{self.course.uuid}/leave/"
        self.url_students = f"/api/v1/courses/{self.course.uuid}/students/"

    def test_list_courses(self):
        """
        Test listing all courses.
        """

        response = self.client.get(self.url_list)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_course(self):
        """
        Test retrieving a single course.
        """

        response = self.client.get(self.url_detail)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_course(self):
        """
        Test creating a new course.
        """

        self.client.login(email=self.instructor_email, password=self.password)

        data = {
            "title": "New Course",
            "description": "New Course Description",
            "category": self.category.uuid,
            "status": Status.ACTIVATE.value,
        }
        response = self.client.post(self.url_list, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("data", response.data)
        self.assertEqual(response.data["data"]["title"], "New Course")

    def test_partial_update_course(self):
        """
        Test partially updating a course.
        """

        self.client.login(email=self.instructor_email, password=self.password)

        data = {"title": "Updated Course Title"}
        response = self.client.patch(self.url_detail, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_enroll_student_in_course(self):
        """
        Test enrolling a student in a course.
        """

        self.client.login(email=self.student_email, password=self.password)

        response = self.client.post(self.url_enroll)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_leave_course(self):
        """
        Test leaving a course.
        """

        self.client.login(email=self.student_email, password=self.password)

        Enrollment.objects.create(course=self.course, student=self.student)
        response = self.client.post(self.url_leave)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_students_in_course(self):
        """
        Test listing all students enrolled in a course.
        """

        Enrollment.objects.create(course=self.course, student=self.student)
        self.client.login(email=self.instructor_email, password=self.password)

        response = self.client.get(self.url_students)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("data", response.data)
        self.assertEqual(len(response.data["data"]), 1)
        self.assertEqual(response.data["data"][0]["uuid"], str(self.student.user.uuid))
