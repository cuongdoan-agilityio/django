from rest_framework import status
from rest_framework.test import APITestCase
from instructors.models import Subject
from instructors.factories import SubjectFactory


class SubjectViewSetTest(APITestCase):
    """
    Test case for the SubjectViewSet.
    """

    def setUp(self):
        """
        Set up the test case with sample subjects.
        """

        SubjectFactory(name="Mathematics")
        SubjectFactory(name="Physics")

        self.url = "/api/v1/subjects/"

    def test_list_subjects(self):
        """
        Test listing all subjects.
        """

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

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
