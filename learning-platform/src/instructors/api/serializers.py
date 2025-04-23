from rest_framework import serializers

from accounts.models import Subject
from instructors.models import Instructor

from django.contrib.auth import get_user_model


User = get_user_model()


class InstructorBaseSerializer(serializers.ModelSerializer):
    """
    Serializer for Instructor serializer.
    """

    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()

    class Meta:
        model = Instructor
        fields = ["id", "first_name", "last_name", "email"]

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
        fields = ["id", "name", "description"]
