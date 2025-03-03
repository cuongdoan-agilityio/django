from rest_framework import serializers
from django.contrib.auth import get_user_model


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
