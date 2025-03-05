from rest_framework import serializers

from core.serializers import MetaSerializer
from courses.models import Course


class CourseSerializer(serializers.ModelSerializer):
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


class CourseListSerializer(serializers.Serializer):
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

    data = CourseSerializer(many=True)
    meta = MetaSerializer()

    def to_representation(self, instance):
        data = super().to_representation(instance)
        meta = {
            "pagination": {
                "total": instance.count(),
                "limit": self.paginator.page_size,
                "page": self.paginator.page.start_index(),
            }
        }

        return {"data": data, "meta": MetaSerializer(meta).data}
