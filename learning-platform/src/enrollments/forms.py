from django import forms
from .models import Enrollment

from core.constants import Status
from core.exceptions import ErrorMessage
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
        fields = ["course", "student"]

    def __init__(self, *args, **kwargs):
        """
        Initialize the form.
        """

        super().__init__(*args, **kwargs)
        if not kwargs.get("instance"):
            self.fields["course"].queryset = Course.objects.filter(
                status=Status.ACTIVATE.value, instructor__isnull=False
            )

    def clean(self):
        """
        Custom validation to ensure that a student can only join a class that they have not joined yet.

        Raises:
            ValidationError: If the student is already enrolled in the selected course.
        """
        cleaned_data = super().clean()
        course = cleaned_data.get("course")
        student = cleaned_data.get("student")

        if Enrollment.objects.filter(course=course, student=student).exists():
            self.add_error("student", ErrorMessage.STUDENT_ALREADY_ENROLLED)

        return cleaned_data
