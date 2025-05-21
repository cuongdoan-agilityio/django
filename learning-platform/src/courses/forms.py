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

        if not course or not student:
            return

        if course.status != Status.ACTIVATE.value:
            self.add_error("course", ErrorMessage.INACTIVE_COURSE)

        if not student.is_student:
            self.add_error("student", ErrorMessage.USER_NOT_STUDENT)

        if student and student.enrollments.filter(course=course).exists():
            self.add_error("student", ErrorMessage.STUDENT_ALREADY_ENROLLED)

        return cleaned_data


class EnrollmentInlineForm(forms.ModelForm):
    """
    Custom form for the Enrollment inline to validate conditions.
    """

    class Meta:
        model = Enrollment
        fields = ["student"]

    def clean(self):
        """
        Custom validation for the Enrollment inline form.
        """

        cleaned_data = super().clean()
        student = cleaned_data.get("student")
        course = self.instance.course if self.instance.pk else None

        if self.has_changed():
            if not course:
                course = self.parent_object if hasattr(self, "parent_object") else None

            if course and student:
                if course.status != Status.ACTIVATE.value:
                    raise forms.ValidationError(ErrorMessage.INACTIVE_COURSE)

                if student.enrollments.filter(course=course).exists():
                    raise forms.ValidationError(ErrorMessage.STUDENT_ALREADY_ENROLLED)

        return cleaned_data
