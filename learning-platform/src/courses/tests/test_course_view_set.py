import pytest
from uuid import uuid4
from django.core.cache import cache
from rest_framework import status
from core.constants import Status
from courses.models import Course
from .base import BaseCourseModuleTestCase
from courses.factories import EnrollmentFactory


class TestCourseViewSet(BaseCourseModuleTestCase):
    """
    Test suite for the CourseViewSet.
    """

    fragment = "courses/"

    @pytest.fixture
    def enroll_courses(self, db):
        """
        Create multiple courses for testing top-courses API.
        """

        self.math_course.enrollment_limit = self.music_course.enrollment_limit = 30
        self.math_course.save()
        self.music_course.save()

        EnrollmentFactory.create_batch(30, course=self.math_course)
        EnrollmentFactory.create_batch(20, course=self.music_course)

    def test_list_courses_ok(self, api_client, course_url, fake_course):
        """
        Test listing all courses.
        """

        cache.clear()
        response = api_client.get(course_url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["data"]) == 1

        cache_data = cache.get("course_list:anonymous:")
        response = api_client.get(course_url)
        assert cache_data == response.data

    def test_empty_list_courses_ok(self, api_client, course_url):
        """
        Test listing all courses.
        """

        cache.clear()
        Course.objects.all().delete()

        response = api_client.get(course_url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["data"] == []

    def test_retrieve_course_ok(self, api_client, course_url, fake_course):
        """
        Test retrieving a single course.
        """

        response = api_client.get(f"{course_url}{str(fake_course.id)}/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["data"]["title"] == fake_course.title

    def test_retrieve_not_exists_course(self, api_client, course_url):
        """
        Test retrieving a single course.
        """

        response = api_client.get(f"{course_url}{str(uuid4())}/")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_create_course(
        self,
        api_client,
        authenticated_fake_instructor,
        fake_category,
        faker,
        course_url,
    ):
        """
        Test creating a new course.
        """

        data = {
            "title": faker.sentence(nb_words=6),
            "description": faker.paragraph(nb_sentences=2),
            "category": fake_category.id,
        }
        response = api_client.post(course_url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["data"]["title"] == data["title"]
        assert response.data["data"]["description"] == data["description"]
        assert response.data["data"]["status"] == Status.ACTIVATE.value

    def test_create_course_unauthorized(
        self, api_client, fake_category, authenticated_fake_student, faker, course_url
    ):
        """
        Test creating a new course without logging in.
        """

        data = {
            "title": faker.sentence(nb_words=6),
            "description": faker.paragraph(nb_sentences=2),
            "category": fake_category.id,
        }
        response = api_client.post(course_url, data, format="json")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_create_course_invalid_data(
        self, api_client, authenticated_fake_instructor, faker, course_url
    ):
        """
        Test creating a new course without logging in.
        """

        data = {
            "title": faker.sentence(nb_words=6),
            "description": faker.paragraph(nb_sentences=2),
            "category": str(uuid4()),
        }
        response = api_client.post(course_url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_partial_update_course_ok(
        self,
        api_client,
        math_course,
        authenticated_fake_instructor,
        course_url,
    ):
        """
        Test partially updating a course.
        """

        data = {"title": "Updated Course Title"}
        response = api_client.patch(
            f"{course_url}{str(math_course.id)}/", data, format="json"
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["data"]["title"] == data["title"]

    def test_partial_update_course_unauthorized(
        self,
        api_client,
        math_course,
        authenticated_fake_student,
        course_url,
    ):
        """
        Test partially updating a course without logging in.
        """

        data = {"title": "Unauthorized Update"}
        response = api_client.patch(
            f"{course_url}{str(math_course.id)}/", data, format="json"
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_partial_update_course_invalid_data(
        self,
        api_client,
        authenticated_fake_instructor,
        course_url,
        math_course,
    ):
        """
        Test creating a new course without logging in.
        """

        data = {
            "category": str(uuid4()),
        }
        response = api_client.patch(
            f"{course_url}{str(math_course.id)}/", data, format="json"
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_admin_enroll_student_into_course(
        self,
        api_client,
        authenticated_fake_admin,
        fake_student,
        course_url,
        math_course,
    ):
        """
        Test enrolling a student in a course.
        """

        response = api_client.post(
            f"{course_url}{str(math_course.id)}/enroll/",
            data={
                "student": str(fake_student.id),
            },
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK

    def test_instructor_enroll_course(
        self,
        api_client,
        authenticated_fake_instructor,
        course_url,
        math_course,
    ):
        """
        Test enrolling a student in a course.
        """

        response = api_client.post(
            f"{course_url}{str(math_course.id)}/enroll/", data=None, format="json"
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_student_enroll_course(
        self,
        api_client,
        authenticated_fake_student,
        course_url,
        math_course,
    ):
        """
        Test enrolling a student in a course.
        """

        response = api_client.post(
            f"{course_url}{str(math_course.id)}/enroll/", data=None, format="json"
        )
        assert response.status_code == status.HTTP_200_OK

    def test_enroll_student_in_course_unauthorized(
        self,
        api_client,
        course_url,
        math_course,
    ):
        """
        Test enrolling a student in a course without logging in.
        """

        response = api_client.post(
            f"{course_url}{str(math_course.id)}/enroll/", data=None, format="json"
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_leave_course(
        self,
        api_client,
        fake_student,
        authenticated_fake_student,
        course_url,
        math_course,
    ):
        """
        Test leaving a course as a student.
        """

        math_course.students.add(fake_student)
        response = api_client.post(
            f"{course_url}{str(math_course.id)}/leave/", data=None, format="json"
        )
        assert response.status_code == status.HTTP_200_OK
        assert not math_course.students.filter(id=str(fake_student.id)).exists()

    def test_instructor_leave_course(
        self, api_client, course_url, authenticated_fake_instructor, math_course
    ):
        """
        Test leaving a course without logging in.
        """

        response = api_client.post(
            f"{course_url}{str(math_course.id)}/leave/", data=None, format="json"
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_leave_course_unauthorized(self, api_client, course_url, math_course):
        """
        Test leaving a course without logging in.
        """

        response = api_client.post(
            f"{course_url}{str(math_course.id)}/leave/", data=None, format="json"
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_admin_leave_student_of_course(
        self,
        api_client,
        authenticated_fake_admin,
        fake_student,
        course_url,
        math_course,
    ):
        """
        Test enrolling a student in a course.
        """

        math_course.students.add(fake_student)

        response = api_client.post(
            f"{course_url}{str(math_course.id)}/leave/",
            data={"student": str(fake_student.id)},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK

    def test_student_leave_unenrolled_course(
        self,
        api_client,
        authenticated_fake_student,
        course_url,
        math_course,
    ):
        """
        Test leave course, which not enrolled.
        """

        response = api_client.post(
            f"{course_url}{str(math_course.id)}/leave/", data=None, format="json"
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_list_students_in_course(
        self,
        api_client,
        fake_student,
        authenticated_fake_instructor,
        disconnect_send_verify_email_signal,
        music_course,
        course_url,
    ):
        """
        Test listing students in a course as an instructor.
        """

        music_course.students.add(fake_student)
        response = api_client.get(f"{course_url}{str(music_course.id)}/students/")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["data"]) == 1

    def test_list_students_in_course_unauthorized(
        self,
        api_client,
        authenticated_fake_student,
        music_course,
        course_url,
    ):
        """
        Test listing students in a course without logging in.
        """

        response = api_client.get(f"{course_url}{str(music_course.id)}/students/")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_filter_courses_by_status_ok(
        self, api_client, math_course, music_course, fake_course, course_url
    ):
        """
        Test filtering courses by status.
        """

        math_course.status = Status.ACTIVATE.value
        math_course.save()
        music_course.status = Status.ACTIVATE.value
        music_course.save()
        fake_course.status = Status.INACTIVE.value
        fake_course.save()

        response = api_client.get(f"{course_url}?status={Status.ACTIVATE.value}")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["data"]) == 2
        assert response.data["data"][0]["status"] == Status.ACTIVATE.value
        assert response.data["data"][1]["status"] == Status.ACTIVATE.value
        assert str(fake_course.id) not in [
            item.get("id") for item in response.data["data"]
        ]

    def test_filter_courses_by_search_ok(
        self, api_client, math_course, music_course, fake_course, course_url
    ):
        """
        Test filtering courses by title.
        """

        math_course.title = "Math course"
        math_course.save()
        music_course.title = "Music course"
        music_course.save()
        fake_course.title = "Python course"
        fake_course.save()

        response = api_client.get(f"{course_url}?search=Python")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["data"]) == 1
        assert "Python" in response.data["data"][0]["title"]
        assert str(fake_course.id) == response.data["data"][0]["id"]

    def test_filter_courses_by_category_ok(
        self,
        api_client,
        fake_category,
        math_course,
        course_url,
    ):
        """
        Test filtering courses by category.
        """

        cache.clear()
        math_course.category = fake_category
        math_course.save()

        response = api_client.get(f"{course_url}?category={str(fake_category.id)}")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["data"]) == 1
        assert response.data["data"][0]["category"]["id"] == str(fake_category.id)

    def test_filter_courses_by_enrolled_ok(
        self,
        api_client,
        fake_student,
        course_url,
        authenticated_fake_student,
        math_course,
    ):
        """
        Test filtering courses by enrolled status.
        """

        math_course.students.add(fake_student)
        response = api_client.get(f"{course_url}?enrolled=true")

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["data"]) == 1
        assert response.data["data"][0]["id"] == str(math_course.id)

    def test_get_top_courses_success(self, enroll_courses):
        """
        Test fetching the top courses successfully.
        """

        cache.clear()
        url = f"{self.fragment}top/"
        response = self.get_json(fragment=url)
        data = response.data["data"]
        list_of_title = [item.get("title") for item in data]

        assert response.status_code == status.HTTP_200_OK
        assert "Math course" in list_of_title
        assert "Music Course" in list_of_title

    def test_get_top_courses_empty(self):
        """
        Test fetching top courses when there are no courses.
        """

        Course.objects.all().delete()
        cache.clear()

        url = f"{self.fragment}top/"
        response = self.get_json(fragment=url)
        data = response.data["data"]

        assert response.status_code == status.HTTP_200_OK
        assert len(data) == 0

        cache_data = cache.get("top_courses")
        response = self.get_json(fragment=url)
        assert cache_data == response.data
