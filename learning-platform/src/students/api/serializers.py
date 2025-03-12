from rest_framework import serializers
from django.contrib.auth import get_user_model


User = get_user_model()


class StudentBaseSerializer(serializers.ModelSerializer):
    """
    Base serializer for student data.
    """

    class Meta:
        model = User
        fields = [
            "uuid",
            "username",
            "first_name",
            "last_name",
            "email",
        ]


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

        return obj.student_profile.scholarship
