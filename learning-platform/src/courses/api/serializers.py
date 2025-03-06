from rest_framework import serializers

from core.serializers import MetaSerializer
from core.constants import Status
from courses.models import Course
from categories.models import Category


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

    class Meta:
        model = Course
        fields = ["uuid", "title", "description", "category", "instructor", "status"]
        read_only_fields = ["uuid", "instructor"]


class CourseListSerializer(serializers.Serializer):
    """
    Serializer for a list of courses with pagination metadata.
    """

    data = CourseDataSerializer(many=True)
    meta = MetaSerializer()


class CourseSerializer(serializers.Serializer):
    """
    Serializer for course detail.
    """

    data = CourseDataSerializer()


class CourseCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for handling create course requests.
    """

    status = serializers.ChoiceField(
        choices=Status.choices(), default=Status.ACTIVATE.value
    )

    class Meta:
        model = Course
        fields = [
            "title",
            "description",
            "category",
            "status",
        ]

    def create(self, validated_data, instructor):
        """
        Creates a new course.

        Args:
            validated_data (dict): The validated data for creating the course.
            instructor (Instructor): The instructor instance.

        Returns:
            Course: The created course instance.
        """

        course = Course.objects.create(
            **validated_data,
            instructor=instructor,
        )
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
            raise serializers.ValidationError(f"Category {value} does not exist.")

        return value
