from rest_framework import serializers

from enrollments.models import Enrollment


class EnrollmentSerializer(serializers.ModelSerializer[Enrollment]):
    """
    Enrollment serializer
    """

    class Meta:
        model = Enrollment
        fields = [
            "course",
            "student",
        ]
