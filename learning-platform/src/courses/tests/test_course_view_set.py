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

    def test_list_courses_ok(self):
        """
        Test listing all courses.
        """

        cache.clear()
        self.auth = None
        response = self.get_json(self.fragment)
        cache_data = cache.get("course_list:anonymous:")
        response = self.get_json(self.fragment)

        assert response.status_code == status.HTTP_200_OK
        assert cache_data == response.data

    def test_empty_list_courses_ok(self):
        """
        Test listing all courses.
        """

        cache.clear()
        Course.objects.all().delete()

        response = self.get_json(self.fragment)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["data"] == []

    def test_filter_courses_by_status_ok(self):
        """
        Test filtering courses by status.
        """

        self.math_course.status = Status.ACTIVATE.value
        self.math_course.save()
        self.music_course.status = Status.ACTIVATE.value
        self.music_course.save()
        self.fake_course.status = Status.INACTIVE.value
        self.fake_course.save()
        response = self.get_json(
            fragment=f"{self.fragment}?status={Status.ACTIVATE.value}"
        )

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["data"]) == 2
        assert response.data["data"][0]["status"] == Status.ACTIVATE.value
        assert response.data["data"][1]["status"] == Status.ACTIVATE.value
        assert str(self.fake_course.id) not in [
            item.get("id") for item in response.data["data"]
        ]

    def test_filter_courses_by_search_ok(self):
        """
        Test filtering courses by title.
        """

        self.math_course.title = "Math course"
        self.math_course.save()
        self.music_course.title = "Music course"
        self.music_course.save()
        self.fake_course.title = "Python course"
        self.fake_course.save()

        response = self.get_json(f"{self.fragment}?search=Python")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["data"]) == 1
        assert "Python" in response.data["data"][0]["title"]
        assert str(self.fake_course.id) == response.data["data"][0]["id"]

    def test_filter_courses_by_category_ok(self):
        """
        Test filtering courses by category.
        """

        cache.clear()
        self.math_course.category = self.fake_category
        self.math_course.save()

        response = self.get_json(
            f"{self.fragment}?category={str(self.fake_category.id)}"
        )
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["data"]) == 1
        assert response.data["data"][0]["category"]["id"] == str(self.fake_category.id)

    def test_filter_courses_by_enrolled_ok(self):
        """
        Test filtering courses by enrolled status.
        """

        self.math_course.students.add(self.fake_student)
        response = self.get_json(f"{self.fragment}?enrolled=true")

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["data"]) == 1
        assert response.data["data"][0]["id"] == str(self.math_course.id)

    def test_retrieve_course_ok(self):
        """
        Test retrieving a single course.
        """

        response = self.get_json(fragment=f"{self.fragment}{str(self.fake_course.id)}/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["data"]["title"] == self.fake_course.title

    def test_retrieve_not_exists_course(self):
        """
        Test retrieving a single course.
        """

        response = self.get_json(fragment=f"{self.fragment}{str(uuid4())}/")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_create_course(self):
        """
        Test creating a new course.
        """

        self.authenticated_token = self.fake_instructor_token
        data = {
            "title": self.faker.sentence(nb_words=6),
            "description": self.faker.paragraph(nb_sentences=2),
            "category": self.fake_category.id,
        }
        response = self.post_json(fragment=self.fragment, data=data)

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["data"]["title"] == data["title"]
        assert response.data["data"]["description"] == data["description"]
        assert response.data["data"]["status"] == Status.ACTIVATE.value

    def test_create_course_unauthorized(self):
        """
        Test creating a new course without logging in.
        """

        data = {
            "title": self.faker.sentence(nb_words=6),
            "description": self.faker.paragraph(nb_sentences=2),
            "category": self.fake_category.id,
        }
        response = self.post_json(fragment=self.fragment, data=data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_create_course_invalid_data(self):
        """
        Test creating a new course without logging in.
        """

        self.authenticated_token = self.fake_instructor_token
        data = {
            "title": self.faker.sentence(nb_words=6),
            "description": self.faker.paragraph(nb_sentences=2),
            "category": str(uuid4()),
        }
        response = self.post_json(fragment=self.fragment, data=data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_partial_update_course_ok(self):
        """
        Test partially updating a course.
        """

        self.authenticated_token = self.fake_instructor_token
        data = {"title": "Updated Course Title"}
        response = self.patch_json(
            fragment=f"{self.fragment}{str(self.math_course.id)}/", data=data
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["data"]["title"] == data["title"]

    def test_partial_update_course_unauthorized(self):
        """
        Test partially updating a course without logging in.
        """

        data = {"title": "Unauthorized Update"}
        response = self.patch_json(
            fragment=f"{self.fragment}{str(self.math_course.id)}/", data=data
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_partial_update_course_invalid_data(self):
        """
        Test creating a new course without logging in.
        """

        self.authenticated_token = self.fake_instructor_token
        data = {
            "category": str(uuid4()),
        }
        response = self.patch_json(
            fragment=f"{self.fragment}{str(self.math_course.id)}/", data=data
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_admin_enroll_student_into_course(self):
        """
        Test enrolling a student in a course.
        """

        self.authenticated_token = self.fake_admin_token
        response = self.post_json(
            fragment=f"{self.fragment}{str(self.math_course.id)}/enroll/",
            data={
                "student": str(self.fake_student.id),
            },
        )
        assert response.status_code == status.HTTP_200_OK

    def test_instructor_enroll_course(self):
        """
        Test enrolling a student in a course.
        """

        self.authenticated_token = self.fake_instructor_token
        response = self.post_json(
            fragment=f"{self.fragment}{str(self.math_course.id)}/enroll/", data=None
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_student_enroll_course(self):
        """
        Test enrolling a student in a course.
        """

        response = self.post_json(
            fragment=f"{self.fragment}{str(self.math_course.id)}/enroll/", data=None
        )
        assert response.status_code == status.HTTP_200_OK

    def test_enroll_student_in_course_unauthorized(self):
        """
        Test enrolling a student in a course without logging in.
        """

        self.auth = "invalid_auth_token"
        response = self.post_json(
            fragment=f"{self.fragment}{str(self.math_course.id)}/enroll/", data=None
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_leave_course(self):
        """
        Test leaving a course as a student.
        """

        self.math_course.students.add(self.fake_student)
        response = self.post_json(
            fragment=f"{self.fragment}{str(self.math_course.id)}/leave/", data=None
        )
        assert response.status_code == status.HTTP_200_OK
        assert not self.math_course.students.filter(
            id=str(self.fake_student.id)
        ).exists()

    def test_instructor_leave_course(self):
        """
        Test leaving a course without logging in.
        """
        self.authenticated_token = self.fake_instructor_token
        response = self.patch_json(
            fragment=f"{self.fragment}{str(self.math_course.id)}/leave/", data=None
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_leave_course_unauthorized(self):
        """
        Test leaving a course without logging in.
        """
        self.auth = "invalid_auth_token"
        response = self.post_json(
            fragment=f"{self.fragment}{str(self.math_course.id)}/leave/", data=None
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_admin_leave_student_of_course(self):
        """
        Test enrolling a student in a course.
        """
        self.authenticated_token = self.fake_admin_token
        self.math_course.students.add(self.fake_student)

        response = self.post_json(
            fragment=f"{self.fragment}{str(self.math_course.id)}/leave/",
            data={"student": str(self.fake_student.id)},
        )
        assert response.status_code == status.HTTP_200_OK

    def test_student_leave_unenrolled_course(self):
        """
        Test leave course, which not enrolled.
        """
        self.math_course.students.remove(self.fake_student)
        response = self.post_json(
            fragment=f"{self.fragment}{str(self.math_course.id)}/leave/",
            data=None,
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_list_students_in_course(self):
        """
        Test listing students in a course as an instructor.
        """

        self.authenticated_token = self.fake_instructor_token
        self.music_course.students.add(self.fake_student)
        response = self.get_json(
            fragment=f"{self.fragment}{str(self.music_course.id)}/students/"
        )

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["data"]) == 1

    def test_list_students_in_course_unauthorized(self):
        """
        Test listing students in a course without logging in.
        """

        response = self.get_json(
            fragment=f"{self.fragment}{str(self.music_course.id)}/students/"
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

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
