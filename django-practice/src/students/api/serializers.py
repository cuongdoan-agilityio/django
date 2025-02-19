from rest_framework import serializers

from students.models import Student


class StudentSerializer(serializers.ModelSerializer[Student]):
    """
    Student serializer
    """

    class Meta:
        model = Student
        fields = ["username", "first name", "last name", "email"]
