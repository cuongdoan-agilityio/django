from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from core.constants import Gender
from courses.models import Course

User = get_user_model()


class CourseViewSetTests(APITestCase):
    """
    Unit tests for the CourseViewSet class.
    """

    def setUp(self):
        """
        Set up the test data.
        """
        self.student_user = User.objects.create_user(
            username="studentuser",
            first_name="Student",
            last_name="User",
            email="student@example.com",
            password="password1234",
            phone_number="1234567890",
            date_of_birth="1990-01-01",
            gender=Gender.MALE.value,
        )
        self.course1 = Course.objects.create(
            uuid="5d5e6e5b-0c5e-4c4f-9b2f-7e7f9e8f4f6e",
            title="Course title1",
            description="Course description1",
            category="Course Category name1",
            instructor="Instructor name",
            status="activate",
        )
        self.course2 = Course.objects.create(
            uuid="5d5e6e5b-0c5e-4c4f-9b2f-7e7f9e8f4f6e",
            title="Course title",
            description="Course description",
            category="Course Category name",
            instructor="Instructor name",
            status="activate",
        )

    def test_get_courses_list(self):
        """
        Test the get courses list action.
        """
        url = reverse("course-list")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["data"]), 2)
        self.assertEqual(response.data["data"][0]["title"], "Course title1")
        self.assertEqual(response.data["data"][1]["title"], "Course title")

    def test_get_courses_list_with_pagination(self):
        """
        Test the get courses list action with pagination.
        """
        url = reverse("course-list") + "?limit=1&offset=1"
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["data"]), 1)
        self.assertEqual(response.data["data"][0]["title"], "Course title")

    def test_get_courses_list_with_filter(self):
        """
        Test the get courses list action with filter.
        """
        url = reverse("course-list") + "?category=Course Category name1"
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["data"]), 1)
        self.assertEqual(response.data["data"][0]["title"], "Course title1")

    def test_get_courses_list_with_enrolled_filter(self):
        """
        Test the get courses list action with enrolled filter.
        """
        self.client.login(username="studentuser", password="password1234")
        url = reverse("course-list") + "?enrolled=true"
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["data"]), 0)

    def test_get_course_detail(self):
        """
        Test the get course detail action.
        """
        url = reverse("course-detail", args=[self.course1.uuid])
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["uuid"], str(self.course1.uuid))
        self.assertEqual(response.data["title"], "Course title1")
