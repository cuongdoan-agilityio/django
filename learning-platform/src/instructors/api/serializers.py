from rest_framework import serializers

from instructors.models import Instructor


class InstructorSerializer(serializers.ModelSerializer[Instructor]):
    """
    Student serializer
    """

    class Meta:
        model = Instructor
        fields = ["user", "subjects", "degree"]
