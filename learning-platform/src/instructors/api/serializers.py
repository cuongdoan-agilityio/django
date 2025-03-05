from rest_framework import serializers

from instructors.models import Instructor

from django.contrib.auth import get_user_model


User = get_user_model()


class InstructorSerializer(serializers.ModelSerializer[Instructor]):
    """
    Student serializer
    """

    class Meta:
        model = Instructor
        fields = ["user", "subjects", "degree"]


class InstructorProfileDataSerializer(serializers.ModelSerializer):
    """
    Serializer for instructor profiles data.
    """

    subjects = serializers.SerializerMethodField()
    degree = serializers.SerializerMethodField()

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
            "degree",
            "subjects",
        ]

    def get_degree(self, obj) -> str | None:
        """
        Retrieves the instructor degree.
        """

        return (
            obj.instructor_profile.degree
            if hasattr(obj, "instructor_profile")
            else None
        )

    def get_subjects(self, obj) -> list[str] | None:
        """
        Retrieves the instructor subjects.
        """

        return (
            [subject.uuid for subject in obj.instructor_profile.subjects.all()]
            if hasattr(obj, "instructor_profile")
            else None
        )


class InstructorProfileSerializer(serializers.Serializer):
    """
    Serializer for instructor profiles.
    """

    data = InstructorProfileDataSerializer()
