from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

from core.constants import ScholarshipChoices, Degree
from accounts.validators import validate_phone_number as check_phone_number
from core.exceptions import ErrorMessage
from students.models import Student
from instructors.models import Subject
from datetime import date

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


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating user profiles.
    """

    scholarship = serializers.ChoiceField(
        choices=ScholarshipChoices.choices(), required=False
    )
    degree = serializers.ChoiceField(choices=Degree.choices(), required=False)
    subjects = serializers.ListField(child=serializers.CharField(), required=False)

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
            "subjects",
        ]

    def validate_subjects(self, value):
        """
        Validates the subjects field.
        """

        for subject in value:
            if not Subject.objects.filter(uuid=subject).exists():
                raise serializers.ValidationError(ErrorMessage.SUBJECT_NOT_EXIST)
        return value

    def validate_phone_number(self, value):
        """
        Validates the phone_number field.
        """

        return check_phone_number(value)

    def validate_date_of_birth(self, value):
        """
        Validates the date_of_birth field based on the user's.
        """

        today = date.today()
        age = (
            today.year
            - value.year
            - ((today.month, today.day) < (value.month, value.day))
        )

        if hasattr(self.instance, "student_profile"):
            if age < 6 or age > 100:
                raise serializers.ValidationError(ErrorMessage.INVALID_STUDENT_AGE)
        elif hasattr(self.instance, "instructor_profile"):
            if age < 18 or age > 100:
                raise serializers.ValidationError(ErrorMessage.INVALID_INSTRUCTOR_AGE)
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

        if "scholarship" in validated_data and hasattr(instance, "student_profile"):
            instance.student_profile.scholarship = validated_data["scholarship"]
            instance.student_profile.save()

        if "degree" in validated_data and hasattr(instance, "instructor_profile"):
            instance.instructor_profile.degree = validated_data["degree"]
            instance.instructor_profile.save()

        if "subjects" in validated_data and hasattr(instance, "instructor_profile"):
            instance.instructor_profile.subjects.set(validated_data["subjects"])
            instance.instructor_profile.save()

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
            "uuid",
            "username",
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "date_of_birth",
            "gender",
        ]
