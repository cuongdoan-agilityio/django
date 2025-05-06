from rest_framework import status

from accounts.factories import UserFactory
from core.constants import Status, Role
from core.tests.base import BaseTestCase
from courses.factories import CourseFactory, CategoryFactory, EnrollmentFactory
from courses.models import Enrollment, Course


class CourseViewSetTest(BaseTestCase):
    """
    Test case for the CourseViewSet.
    """

    def setUp(self):
        """
        Set up the test case with sample data.
        """

        super().setUp()

        self.course_title = self.fake.sentence(nb_words=6)
        self.course_description = self.fake.paragraph(nb_sentences=2)
        self.course = CourseFactory(
            title=self.course_title,
            instructor=self.instructor_user,
            status=Status.ACTIVATE.value,
            description=self.course_description,
        )

        self.url_list = f"{self.root_url}courses/"
        self.url_detail = f"{self.root_url}courses/{self.course.id}/"
        self.url_enroll = f"{self.root_url}courses/{self.course.id}/enroll/"
        self.url_leave = f"{self.root_url}courses/{self.course.id}/leave/"
        self.url_students = f"{self.root_url}courses/{self.course.id}/students/"
        self.url_top_courses = f"{self.root_url}courses/top/"

    def tearDown(self):
        """
        Clean up the test case by deleting the created course and enrollments.
        """
        super().tearDown()
        Enrollment.objects.all().delete()

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

        data = {
            "title": self.fake.sentence(nb_words=6),
            "description": self.fake.paragraph(nb_sentences=2),
            "category": self.category.id,
        }

        response = self.post_json(
            url=self.url_list,
            data=data,
            email=self.instructor_email,
        )
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
            "category": self.category.id,
        }
        response = self.post_json(
            url=self.url_list,
            data=data,
            email=self.email,
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_partial_update_course_ok(self):
        """
        Test partially updating a course.
        """

        data = {"title": self.fake.sentence(nb_words=6)}
        response = self.patch_json(
            url=self.url_detail,
            data=data,
            email=self.instructor_email,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["title"], data.get("title"))
        self.assertEqual(response.data["data"]["status"], Status.ACTIVATE.value)

    def test_partial_update_course_unauthorized(self):
        """
        Test partially updating a course without logging in.
        """

        data = {"title": self.fake.sentence(nb_words=6)}
        response = self.patch_json(
            url=self.url_detail,
            data=data,
            email=self.email,
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_enroll_student_in_course(self):
        """
        Test enrolling a student in a course.
        """

        response = self.post_json(
            url=self.url_enroll,
            data=None,
            email=self.email,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_enroll_student_in_course_unauthorized(self):
        """
        Test enrolling a student in a course without logging in.
        """

        response = self.post_json(
            url=self.url_enroll,
            data=None,
            email=self.instructor_email,
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_leave_course(self):
        """
        Test leaving a course.
        """

        Enrollment.objects.create(course=self.course, student=self.student_user)
        response = self.post_json(
            url=self.url_leave,
            data=None,
            email=self.email,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_leave_course_unauthorized(self):
        """
        Test leaving a course without logging in.
        """

        Enrollment.objects.create(course=self.course, student=self.student_user)
        response = self.post_json(
            url=self.url_leave,
            data=None,
            email=self.instructor_email,
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_students_in_course(self):
        """
        Test listing all students enrolled in a course.
        """

        Enrollment.objects.create(course=self.course, student=self.student_user)
        response = self.get_json(
            url=self.url_students,
            email=self.instructor_email,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("data", response.data)
        self.assertEqual(len(response.data["data"]), 1)
        self.assertEqual(response.data["data"][0]["id"], str(self.student_user.id))

    def test_list_students_in_course_unauthorized(self):
        """
        Test listing all students enrolled in a course without logging in.
        """

        Enrollment.objects.create(course=self.course, student=self.student_user)
        response = self.get_json(
            url=self.url_students,
            email=self.email,
        )
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

        response = self.client.get(self.url_list, {"category": new_category.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["data"]), 1)
        self.assertEqual(
            response.data["data"][0]["category"]["id"], str(new_category.id)
        )

    def test_filter_courses_by_enrolled_ok(self):
        """
        Test filtering courses by enrollment status.
        """

        Enrollment.objects.create(course=self.course, student=self.student_user)

        self.client.login(email=self.email, password=self.password)

        response = self.client.get(self.url_list, {"enrolled": True})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["data"]), 1)
        self.assertEqual(response.data["data"][0]["title"], self.course_title)

    def create_courses(self):
        """
        Create multiple courses for testing top-courses API.
        """

        new_instructor = UserFactory(
            username=self.fake.user_name(), role=Role.INSTRUCTOR.value
        )
        self.another_course_description = self.fake.paragraph(nb_sentences=2)
        self.another_course_title = self.fake.sentence(nb_words=6)
        self.another_course = CourseFactory(
            title=self.another_course_title,
            description=self.another_course_description,
            status=Status.ACTIVATE.value,
            instructor=new_instructor,
        )

        EnrollmentFactory.create_batch(30, course=self.course)
        EnrollmentFactory.create_batch(20, course=self.another_course)

    def test_get_top_courses_success(self):
        """
        Test retrieving the top courses successfully.
        """
        self.create_courses()

        response = self.client.get(self.url_top_courses)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("data", response.data)
        self.assertEqual(len(response.data["data"]), 2)
        self.assertEqual(response.data["data"][0]["title"], self.course_title)
        self.assertEqual(
            response.data["data"][0]["description"], self.course_description
        )
        self.assertEqual(response.data["data"][1]["title"], self.another_course_title)
        self.assertEqual(
            response.data["data"][1]["description"], self.another_course_description
        )

    def test_get_top_courses_empty(self):
        """
        Test retrieving top courses when no courses exist.
        """
        Course.objects.all().delete()
        response = self.client.get(self.url_top_courses)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("data", response.data)
        self.assertEqual(len(response.data["data"]), 0)

    def test_get_top_courses_unauthenticated(self):
        """
        Test retrieving top courses without authentication.
        """
        response = self.client.get(self.url_top_courses)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_top_courses_invalid_http_method(self):
        """
        Test using an invalid HTTP method for the top_courses API.
        """
        response = self.post_json(
            url=self.url_top_courses,
            data=None,
            email=self.instructor_email,
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
