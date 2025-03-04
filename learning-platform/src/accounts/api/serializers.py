from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

from core.constants import ScholarshipChoices
from students.models import Student

User = get_user_model()


class LoginRequestSerializer(serializers.Serializer):
    """
    Serializer for handling login requests.

    Fields:
        email (CharField): The email of the user.
        password (CharField): The password of the user (write-only).
    """

    email = serializers.CharField()
    password = serializers.CharField(write_only=True)


class LoginResponseDataSerializer(serializers.Serializer):
    """
    Serializer for the data in the login response.

    Fields:
        token (CharField): The authentication token for the user.
    """

    token = serializers.CharField()


class LoginResponseSerializer(serializers.Serializer):
    """
    Serializer for the login response.

    Fields:
        data (LoginResponseDataSerializer): The data containing the authentication token.
    """

    data = LoginResponseDataSerializer()


class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for handling user registration requests.
    """

    password = serializers.CharField(write_only=True, validators=[validate_password])

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password",
        ]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        """
        Creates a new user and associated student profile.

        Args:
            validated_data (dict): The validated data for creating the user and student profile.

        Returns:
            User: The created user instance.
        """

        user = User.objects.create_user(**validated_data)
        Student.objects.create(user=user, scholarship=ScholarshipChoices.ZERO.value)
        return user
