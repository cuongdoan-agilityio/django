from rest_framework import serializers
from django.contrib.auth import get_user_model

from core.serializers import MetaSerializer


User = get_user_model()


class StudentBaseSerializer(serializers.ModelSerializer):
    """
    Base serializer for student data.
    """

    uuid = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "uuid",
            "username",
            "first_name",
            "last_name",
            "email",
        ]

    def get_uuid(self, obj) -> str:
        """
        Retrieves the student uuid.
        """

        self.check_user(obj)
        return obj.student_profile.uuid

    def check_user(self, obj) -> None:
        """
        Raise an error if the user is not a student.
        """

        if not hasattr(obj, "student_profile"):
            raise serializers.ValidationError("User is not a student.")


class StudentProfileDataSerializer(StudentBaseSerializer):
    """
    Serializer for student profile data.
    """

    scholarship = serializers.SerializerMethodField()

    class Meta(StudentBaseSerializer.Meta):
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

        self.check_user(obj)
        return obj.student_profile.scholarship


class StudentProfileSerializer(serializers.Serializer):
    """
    Serializer for student profile.
    """

    data = StudentProfileDataSerializer(many=True)


class StudentListSerializer(serializers.Serializer):
    """
    Serializer for a list of student profiles with pagination metadata.
    """

    data = StudentBaseSerializer(many=True)
    meta = MetaSerializer()
