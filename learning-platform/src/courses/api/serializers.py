from rest_framework import serializers

from courses.models import Course


class CourseSerializer(serializers.ModelSerializer[Course]):
    """
    Student serializer
    """

    class Meta:
        model = Course
        fields = ["title", "description", "category", "instructor"]
