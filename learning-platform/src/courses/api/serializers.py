from rest_framework import serializers

from core.constants import Status
from core.error_messages import ErrorMessage
from core.serializers import MetaSerializer
from courses.models import Course, Category

from accounts.api.serializers import UserBaseSerializer


class CategorySerializer(serializers.ModelSerializer):
    """
    Serializer for the Category model.
    """

    class Meta:
        model = Category
        fields = ["id", "name", "description", "modified"]


class CategoryListSerializer(serializers.Serializer):
    data = CategorySerializer(many=True)
    meta = MetaSerializer()


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
        fields = [
            "id",
            "title",
            "description",
            "category",
            "instructor",
            "status",
            "modified",
        ]
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

    def validate(self, data):
        """
        Validates the instructor value.
        """

        request = self.context.get("request")

        if (
            request
            and request.user
            and request.user.is_superuser
            and not data.get("instructor")
        ):
            raise serializers.ValidationError(
                {"instructor": ErrorMessage.INSTRUCTOR_DATA_REQUIRED}
            )

        return data


class EnrollmentCreateOrEditSerializer(serializers.Serializer):
    """
    Serializer for handling enroll course.
    """

    student = serializers.UUIDField(
        required=False, help_text="The UUID of the student."
    )

    def validate(self, data):
        """
        Validates the instructor value.
        """

        request = self.context.get("request")

        if (
            request
            and request.user
            and request.user.is_superuser
            and not data.get("student")
        ):
            raise serializers.ValidationError(
                {"student": ErrorMessage.STUDENT_DATA_REQUIRED}
            )

        return data


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


class CourseStudentResponseSerializer(serializers.Serializer):
    """
    Serializer for course student response.
    """

    data = UserBaseSerializer(many=True)
    meta = MetaSerializer()
