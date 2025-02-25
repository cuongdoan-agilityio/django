from django import forms
from .models import Enrollment

from core.constants import Status
from courses.models import Course


class EnrollmentForm(forms.ModelForm):
    """
    Custom form for the Enrollment model to handle validation.

    Fields:
        course (ModelChoiceField): The course that the student is enrolling in.
        student (ModelChoiceField): The student who is enrolling in the course.
    """

    class Meta:
        model = Enrollment
        fields = ["course", "student", "enrolled_at"]

    def __init__(self, *args, **kwargs):
        """
        Initialize the form and disable the course and student fields if editing an existing instance.
        """
        super().__init__(*args, **kwargs)
        if kwargs.get("instance"):
            self.fields["course"].disabled = True
            self.fields["student"].disabled = True
            self.fields["enrolled_at"].disabled = True
        else:
            self.fields["course"].queryset = Course.objects.filter(
                status=Status.ACTIVATE.value, instructor__isnull=False
            )

    def clean(self):
        """
        Custom validation to ensure that a student can only join a class that they have not joined yet.
        """
        cleaned_data = super().clean()
        course = cleaned_data.get("course")
        student = cleaned_data.get("student")

        if Enrollment.objects.filter(course=course, student=student).exists():
            self.add_error(
                "student", "This student is already enrolled in this course."
            )

        return cleaned_data
