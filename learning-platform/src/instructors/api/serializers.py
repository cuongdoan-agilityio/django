from rest_framework import serializers

from instructors.models import Subject, Instructor

from django.contrib.auth import get_user_model


User = get_user_model()


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

        return obj.instructor_profile.degree

    def get_subjects(self, obj) -> list[str] | None:
        """
        Retrieves the instructor subjects.
        """

        return [subject.uuid for subject in obj.instructor_profile.subjects.all()]


class InstructorBaseSerializer(serializers.ModelSerializer):
    """
    Serializer for Instructor serializer.
    """

    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()

    class Meta:
        model = Instructor
        fields = ["uuid", "first_name", "last_name", "email"]

    def get_first_name(self, obj) -> str | None:
        """
        Retrieves the instructor first name.
        """

        return obj.user.first_name

    def get_last_name(self, obj) -> str | None:
        """
        Retrieves the instructor last name.
        """

        return obj.user.last_name

    def get_email(self, obj) -> str:
        """
        Retrieves the instructor email.
        """

        return obj.user.email


class SubjectSerializer(serializers.ModelSerializer):
    """
    Subject serializer
    """

    class Meta:
        model = Subject
        fields = ["uuid", "name", "description"]
