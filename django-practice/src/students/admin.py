from django.contrib import admin

from .forms import StudentCreationForm
from .models import Student


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    """
    Custom admin class for the Student model.

    Displays user-related fields in the admin interface and handles the creation of a user when creating a student.
    """

    list_display = [
        "username",
        "first_name",
        "last_name",
        "email",
        "phone_number",
        "date_of_birth",
        "gender",
    ]

    form = StudentCreationForm

    def username(self, obj):
        """
        Returns the username of the user associated with the student.
        """

        return obj.user.username

    def first_name(self, obj):
        """
        Returns the first name of the user associated with the student.
        """

        return obj.user.first_name

    def last_name(self, obj):
        """
        Returns the last name of the user associated with the student.
        """

        return obj.user.last_name

    def email(self, obj):
        """
        Returns the email of the user associated with the student.
        """

        return obj.user.username

    def phone_number(self, obj):
        """
        Returns the phone number of the user associated with the student.
        """

        return obj.user.phone_number

    def date_of_birth(self, obj):
        """
        Returns the date of birth of the user associated with the student.
        """

        return obj.user.date_of_birth

    def gender(self, obj):
        """
        Returns the gender of the user associated with the student.
        """

        return obj.user.gender

    def save_model(self, request, obj, form, change):
        """
        Override the save_model method to create a new user when creating a new student.

        Args:
            request (HttpRequest): The current request object.
            obj (Student): The student instance being saved.
            form (ModelForm): The form instance used to save the student.
            change (bool): Whether this is an update or a new instance.
        """

        if not change:
            user_data = {
                "username": form.cleaned_data["username"],
                "first_name": form.cleaned_data["first_name"],
                "last_name": form.cleaned_data["last_name"],
                "email": form.cleaned_data["email"],
                "phone_number": form.cleaned_data["phone_number"],
                "date_of_birth": form.cleaned_data["date_of_birth"],
                "gender": form.cleaned_data["gender"],
                "password": form.cleaned_data["password"],
            }
            student_form = StudentCreationForm(user_data)
            if student_form.is_valid():
                user = student_form.create_user()
                obj.user = user

        super().save_model(request, obj, form, change)
