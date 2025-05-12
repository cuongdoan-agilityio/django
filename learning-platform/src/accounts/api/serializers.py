from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

from core.constants import ScholarshipChoices, Degree
from core.error_messages import ErrorMessage
from accounts.models import Specialization

User = get_user_model()


class LoginRequestSerializer(serializers.Serializer):
    """
    Serializer for handling login requests.

    Fields:
        email (EmailField): The email of the user.
        password (CharField): The password of the user (write-only).
    """

    email = serializers.EmailField(required=True)
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

        user = User(
            username=validated_data["username"],
            email=validated_data["email"],
            scholarship=ScholarshipChoices.ZERO.value,
            password=validated_data["password"],
        )
        user.full_clean()
        user.save()
        return user


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating user profiles.
    """

    scholarship = serializers.ChoiceField(
        choices=ScholarshipChoices.choices(), required=False
    )
    degree = serializers.ChoiceField(choices=Degree.choices(), required=False)
    specializations = serializers.ListField(
        child=serializers.CharField(), required=False
    )

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "phone_number",
            "date_of_birth",
            "gender",
            "scholarship",
            "degree",
            "specializations",
        ]

    def validate_specializations(self, value):
        """
        Validates the specializations field.
        """

        for specialization in value:
            if not Specialization.objects.filter(id=specialization).exists():
                raise serializers.ValidationError(ErrorMessage.SPECIALIZATION_NOT_EXIST)
        return value

    def update(self, instance, validated_data):
        """
        Updates the user profile with the provided validated data.

        Args:
            instance (User): The user instance to update.
            validated_data (dict): The validated data for updating the user profile.

        Returns:
            User: The updated user instance.
        """

        if "scholarship" in validated_data and instance.is_student:
            instance.scholarship = validated_data["scholarship"]

        if "degree" in validated_data and instance.is_instructor:
            instance.degree = validated_data["degree"]

        if "specializations" in validated_data and instance.is_instructor:
            instance.specializations.set(validated_data["specializations"])

        if "password" not in validated_data:
            instance.password = None

        instance.phone_number = validated_data.get(
            "phone_number", instance.phone_number
        )
        instance.first_name = validated_data.get("first_name", instance.first_name)
        instance.last_name = validated_data.get("last_name", instance.last_name)
        instance.date_of_birth = validated_data.get(
            "date_of_birth", instance.date_of_birth
        )
        instance.gender = validated_data.get("gender", instance.gender)
        instance.save()

        return instance


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for user data.
    """

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "date_of_birth",
            "gender",
        ]


class SpecializationSerializer(serializers.ModelSerializer):
    """
    Specialization serializer
    """

    class Meta:
        model = Specialization
        fields = ["id", "name", "description"]


class UserBaseSerializer(serializers.ModelSerializer):
    """
    Base serializer for user data.
    """

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
        ]


class UserProfileDataSerializer(UserBaseSerializer):
    """
    Serializer for user profile data.
    """

    class Meta(UserBaseSerializer.Meta):
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "date_of_birth",
            "gender",
            "scholarship",
            "role",
            "degree",
            "specializations",
        ]
