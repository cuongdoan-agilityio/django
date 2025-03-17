from rest_framework import serializers

from core.constants import Status
from core.exceptions import ErrorMessage
from courses.models import Course, Category, Enrollment

from instructors.api.serializers import InstructorBaseSerializer


class CategorySerializer(serializers.ModelSerializer):
    """
    Serializer for the Category model.
    """

    class Meta:
        model = Category
        fields = ["uuid", "name", "description"]


class CourseDataSerializer(serializers.ModelSerializer):
    """
    Serializer for course data.

    Fields:
        uuid (UUIDField): The UUID of the course.
        title (CharField): The title of the course.
        description (CharField): The description of the course.
        category (CharField): The category of the course.
        instructor (CharField): The name of the instructor.
        status (CharField): The status of the course.
    """

    instructor = InstructorBaseSerializer()
    category = CategorySerializer()

    class Meta:
        model = Course
        fields = ["uuid", "title", "description", "category", "instructor", "status"]
        read_only_fields = ["instructor"]


class CourseCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for handling create course requests.
    """

    class Meta:
        model = Course
        fields = [
            "title",
            "description",
            "category",
            "status",
            "instructor",
        ]

    def create(self, validated_data):
        """
        Creates a new course.

        Args:
            validated_data (dict): The validated data for creating the course.

        Returns:
            Course: The created course instance.
        """

        course = Course.objects.create(**validated_data)
        return course


class CourseUpdateSerializer(serializers.Serializer):
    """
    Serializer for updating course data.
    """

    status = serializers.ChoiceField(choices=Status.choices(), required=False)
    title = serializers.CharField(required=False)
    description = serializers.CharField(required=False)
    category = serializers.CharField(required=False)

    def validate_category(self, value):
        """
        Validates the category field.
        """

        if not Category.objects.filter(uuid=value).exists():
            raise serializers.ValidationError(ErrorMessage.CATEGORY_NOT_EXIST)

        return value


class EnrollmentSerializer(serializers.ModelSerializer):
    """
    Enrollment serializer
    """

    class Meta:
        model = Enrollment
        fields = [
            "course",
            "student",
        ]
