from django import forms
from .models import Enrollment

from core.constants import Status
from core.error_messages import ErrorMessage


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

    def clean(self):
        """
        Custom validation to ensure that a student can only join a class that they have not joined yet.

        Raises:
            ValidationError: If the student is already enrolled in the selected course.
        """

        cleaned_data = super().clean()
        course = cleaned_data.get("course")
        student = cleaned_data.get("student")

        if not course:
            return

        if course.status != Status.ACTIVATE.value:
            self.add_error("course", ErrorMessage.INACTIVE_COURSE)

        if not course.instructor:
            self.add_error("course", ErrorMessage.COURSE_HAS_NO_INSTRUCTOR)

        if Enrollment.objects.filter(course=course, student=student).exists():
            self.add_error("student", ErrorMessage.STUDENT_ALREADY_ENROLLED)

        return cleaned_data
