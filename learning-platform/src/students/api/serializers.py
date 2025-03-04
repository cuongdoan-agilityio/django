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


class StudentProfileDataSerializer(serializers.ModelSerializer):
    """
    Serializer for student profile data.
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

    def get_scholarship(self, obj) -> int:
        """
        Retrieves the student scholarship.
        """

        if not hasattr(obj, "student_profile"):
            raise serializers.ValidationError("User is not a student.")

        return obj.student_profile.scholarship


class StudentProfileSerializer(serializers.Serializer):
    """
    Serializer for student profile.
    """

    data = StudentProfileDataSerializer()
