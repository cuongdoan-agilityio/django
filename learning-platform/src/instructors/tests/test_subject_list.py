from rest_framework import status
from instructors.models import Subject
from instructors.factories import SubjectFactory
from core.tests.base import BaseTestCase


class SubjectViewSetTest(BaseTestCase):
    """
    Test case for the SubjectViewSet.
    """

    def setUp(self):
        """
        Set up the test case with sample subjects.
        """
        super().setUp()

        Subject.objects.all().delete()
        self.subject_name = self.fake.sentence(nb_words=5)
        self.another_subject_name = self.fake.sentence(nb_words=5)
        SubjectFactory(name=self.subject_name)
        SubjectFactory(name=self.another_subject_name)

        self.url = f"{self.root_url}subjects/"

    def test_list_subjects_ok(self):
        """
        Test listing all subjects.
        """

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data["data"]
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]["name"], self.subject_name)
        self.assertEqual(data[1]["name"], self.another_subject_name)

    def test_list_subjects_empty(self):
        """
        Test listing subjects when there are no subjects.
        """

        Subject.objects.all().delete()
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.data["data"]
        self.assertEqual(data, [])

    def test_subject_viewset_permissions(self):
        """
        Test that the SubjectViewSet allows any user to access the list of subjects.
        """

        self.client.logout()
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_subjects_with_limit_offset(self):
        """
        Test that subjects are listed in alphabetical order by default.
        """

        response = self.client.get(f"{self.url}?limit=5&offset=1")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.data["data"]
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["name"], self.another_subject_name)

        pagination = response.data["meta"]["pagination"]
        self.assertEqual(pagination["limit"], 5)
        self.assertEqual(pagination["offset"], 1)
        self.assertEqual(pagination["total"], 2)

    def test_list_subjects_failed(self):
        """
        Test that the request to list subjects fails due to an invalid URL.
        """

        invalid_url = f"{self.root_url}invalid_subjects/"
        response = self.client.get(invalid_url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
