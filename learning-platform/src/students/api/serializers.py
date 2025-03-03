from rest_framework import serializers
from django.contrib.auth import get_user_model

from students.models import Student


User = get_user_model()


class StudentSerializer(serializers.ModelSerializer[Student]):
    """
    Student serializer
    """

    class Meta:
        model = Student
        fields = ["user", "scholarship"]


class StudentProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for student data.
    """

    scholarship = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "uuid",
            "username",
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "date_of_birth",
            "gender",
            "scholarship",
        ]

    def get_scholarship(self, obj):
        """
        Retrieves the student scholarship.
        """

        return (
            obj.student_profile.scholarship if hasattr(obj, "student_profile") else None
        )
