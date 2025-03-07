from rest_framework import serializers

from instructors.models import Subject

from django.contrib.auth import get_user_model


User = get_user_model()


class InstructorProfileDataSerializer(serializers.ModelSerializer):
    """
    Serializer for instructor profiles data.
    """

    subjects = serializers.SerializerMethodField()
    degree = serializers.SerializerMethodField()
    uuid = serializers.SerializerMethodField()

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

        return obj.instructor_profile.degree

    def get_subjects(self, obj) -> list[str] | None:
        """
        Retrieves the instructor subjects.
        """

        return [subject.uuid for subject in obj.instructor_profile.subjects.all()]

    def get_uuid(self, obj) -> int:
        """
        Retrieves the instructor uuid.
        """

        return obj.instructor_profile.uuid


class InstructorProfileSerializer(serializers.Serializer):
    """
    Serializer for instructor profiles.
    """

    data = InstructorProfileDataSerializer()


class SubjectSerializer(serializers.ModelSerializer):
    """
    Subject serializer
    """

    class Meta:
        model = Subject
        fields = ["uuid", "name"]
