from rest_framework import serializers

from core.constants import Status
from core.error_messages import ErrorMessage
from courses.models import Course, Category, Enrollment

from accounts.api.serializers import UserBaseSerializer


class CategorySerializer(serializers.ModelSerializer):
    """
    Serializer for the Category model.
    """

    class Meta:
        model = Category
        fields = ["id", "name", "description"]


class CourseDataSerializer(serializers.ModelSerializer):
    """
    Serializer for course data.

    Fields:
        id (UUIDField): The UUID of the course.
        title (CharField): The title of the course.
        description (CharField): The description of the course.
        category (CharField): The category of the course.
        instructor (CharField): The name of the instructor.
        status (CharField): The status of the course.
    """

    instructor = UserBaseSerializer()
    category = CategorySerializer()

    class Meta:
        model = Course
        fields = ["id", "title", "description", "category", "instructor", "status"]
        read_only_fields = ["instructor"]


class TopCoursesSerializer(serializers.Serializer):
    """
    Serializer for the top courses.
    """

    data = CourseDataSerializer(many=True)


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


class EnrollmentCreateOrEditSerializer(serializers.Serializer):
    """
    Serializer for handling enroll course.
    """

    student = serializers.UUIDField(
        required=False, help_text="The UUID of the student."
    )


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

        if not Category.objects.filter(id=value).exists():
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

    def validate_course(self, instance):
        """
        Validates the course field.
        """

        if instance.status != "activate":
            raise serializers.ValidationError(ErrorMessage.INACTIVE_COURSE)

        return instance

    def validate(self, data):
        """
        Validates the data before creating an enrollment.

        Args:
            data (dict): The data to validate.

        Returns:
            dict: The validated data.
        """

        course = data.get("course")
        student = data.get("student")

        if student and student.enrollments.filter(course=course).exists():
            raise serializers.ValidationError(
                {"student": ErrorMessage.ALREADY_ENROLLED}
            )

        if course.is_full:
            raise serializers.ValidationError({"course": ErrorMessage.COURSE_IS_FULL})

        return data
