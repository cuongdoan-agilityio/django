from rest_framework import status

from accounts.factories import UserFactory
from core.constants import Status
from courses.factories import CourseFactory, CategoryFactory
from courses.models import Enrollment
from instructors.factories import InstructorFactory
from core.tests.base import BaseTestCase


# fake = Faker()


class CourseViewSetTest(BaseTestCase):
    """
    Test case for the CourseViewSet.
    """

    def setUp(self):
        """
        Set up the test case with sample data.
        """
        super().setUp()

        self.instructor_email = self.fake.email()
        self.instructor_username = self.fake.user_name()
        self.course_title = self.fake.sentence(nb_words=6)
        self.course_description = self.fake.paragraph(nb_sentences=2)

        self.instructor_user = UserFactory(
            username=self.instructor_username,
            email=self.instructor_email,
            password=self.password,
        )
        self.instructor = InstructorFactory(user=self.instructor_user)
        self.course = CourseFactory(
            title=self.course_title,
            instructor=self.instructor,
            status=Status.ACTIVATE.value,
            description=self.course_description,
        )

        self.url_list = f"{self.root_url}courses/"
        self.url_detail = f"{self.root_url}courses/{self.course.uuid}/"
        self.url_enroll = f"{self.root_url}courses/{self.course.uuid}/enroll/"
        self.url_leave = f"{self.root_url}courses/{self.course.uuid}/leave/"
        self.url_students = f"{self.root_url}courses/{self.course.uuid}/students/"

    def test_list_courses_ok(self):
        """
        Test listing all courses.
        """

        response = self.client.get(self.url_list)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_course_ok(self):
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
            "title": self.fake.sentence(nb_words=6),
            "description": self.fake.paragraph(nb_sentences=2),
            "category": self.category.uuid,
        }

        response = self.client.post(self.url_list, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("data", response.data)
        self.assertEqual(response.data["data"]["title"], data.get("title"))
        self.assertEqual(response.data["data"]["description"], data.get("description"))
        self.assertEqual(response.data["data"]["status"], Status.ACTIVATE.value)

    def test_create_course_unauthorized(self):
        """
        Test creating a new course without logging in.
        """

        data = {
            "title": self.fake.sentence(nb_words=6),
            "description": self.fake.paragraph(nb_sentences=2),
            "category": self.category.uuid,
        }

        response = self.client.post(self.url_list, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_partial_update_course_ok(self):
        """
        Test partially updating a course.
        """

        self.client.login(email=self.instructor_email, password=self.password)

        data = {"title": self.fake.sentence(nb_words=6)}
        response = self.client.patch(self.url_detail, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["title"], data.get("title"))
        self.assertEqual(response.data["data"]["status"], Status.ACTIVATE.value)

    def test_partial_update_course_unauthorized(self):
        """
        Test partially updating a course without logging in.
        """

        data = {"title": self.fake.sentence(nb_words=6)}
        response = self.client.patch(self.url_detail, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_enroll_student_in_course(self):
        """
        Test enrolling a student in a course.
        """

        self.client.login(email=self.email, password=self.password)

        response = self.client.post(self.url_enroll)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_enroll_student_in_course_unauthorized(self):
        """
        Test enrolling a student in a course without logging in.
        """

        response = self.client.post(self.url_enroll)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_leave_course(self):
        """
        Test leaving a course.
        """

        self.client.login(email=self.email, password=self.password)

        Enrollment.objects.create(course=self.course, student=self.student_profile)
        response = self.client.post(self.url_leave)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_leave_course_unauthorized(self):
        """
        Test leaving a course without logging in.
        """

        Enrollment.objects.create(course=self.course, student=self.student_profile)
        response = self.client.post(self.url_leave)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_students_in_course(self):
        """
        Test listing all students enrolled in a course.
        """

        Enrollment.objects.create(course=self.course, student=self.student_profile)
        self.client.login(email=self.instructor_email, password=self.password)

        response = self.client.get(self.url_students)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("data", response.data)
        self.assertEqual(len(response.data["data"]), 1)
        self.assertEqual(
            response.data["data"][0]["uuid"], str(self.student_profile.user.uuid)
        )

    def test_list_students_in_course_unauthorized(self):
        """
        Test listing all students enrolled in a course without logging in.
        """

        Enrollment.objects.create(course=self.course, student=self.student_profile)
        response = self.client.get(self.url_students)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_filter_courses_by_status_ok(self):
        """
        Test filtering courses by status.
        """

        CourseFactory(status=Status.INACTIVE.value)
        response = self.client.get(self.url_list, {"status": Status.INACTIVE.value})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["data"]), 1)
        self.assertEqual(response.data["data"][0]["status"], Status.INACTIVE.value)

    def test_filter_courses_by_title_ok(self):
        """
        Test filtering courses by title.
        """

        response = self.client.get(self.url_list, {"title": self.course_title})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["data"]), 1)
        self.assertEqual(response.data["data"][0]["title"], self.course_title)

    def test_filter_courses_by_description_ok(self):
        """
        Test filtering courses by description.
        """

        response = self.client.get(
            self.url_list, {"description": self.course_description}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["data"]), 1)
        self.assertEqual(
            response.data["data"][0]["description"], self.course_description
        )

    def test_filter_courses_by_category_ok(self):
        """
        Test filtering courses by category.
        """

        new_category = CategoryFactory()
        CourseFactory(title="New Category Course", category=new_category)

        response = self.client.get(self.url_list, {"category": new_category.uuid})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["data"]), 1)
        self.assertEqual(
            response.data["data"][0]["category"]["uuid"], str(new_category.uuid)
        )

    def test_filter_courses_by_enrolled_ok(self):
        """
        Test filtering courses by enrollment status.
        """

        Enrollment.objects.create(course=self.course, student=self.student_profile)

        self.client.login(email=self.email, password=self.password)

        response = self.client.get(self.url_list, {"enrolled": True})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["data"]), 1)
        self.assertEqual(response.data["data"][0]["title"], self.course_title)
