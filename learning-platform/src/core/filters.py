from django.contrib import admin

from core.constants import Gender


class GenderFilter(admin.SimpleListFilter):
    """
    Custom filter for the gender field in the Student model.

    This filter allows the admin to filter students based on their gender.

    Attributes:
        title (str): The title of the filter displayed in the admin interface.
        parameter_name (str): The URL parameter used for the filter.
    """

    title = "Gender"
    parameter_name = "gender"

    def lookups(self, request, model_admin):
        """
        Returns the list of filter options.

        Args:
            request (HttpRequest): The current request object.
            model_admin (ModelAdmin): The current model admin instance.

        Returns:
            list: A list of tuples containing the filter options.
        """

        return [
            (Gender.MALE.value, "Male"),
            (Gender.FEMALE.value, "Female"),
            (Gender.OTHER.value, "Other"),
            ("not_set", "Not Set"),
        ]

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the selected filter option.

        Args:
            request (HttpRequest): The current request object.
            queryset (QuerySet): The original queryset.

        Returns:
            QuerySet: The filtered queryset.
        """

        if not self.value():
            return queryset

        if self.value() in [Gender.MALE.value, Gender.FEMALE.value, Gender.OTHER.value]:
            return queryset.filter(user__gender=self.value())

        return queryset.filter(user__gender__isnull=True)
