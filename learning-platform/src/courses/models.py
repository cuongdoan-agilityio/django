from django.db import models
from django.core.exceptions import ValidationError

from core.models import AbstractBaseModel
from core.constants import Status
from core.error_messages import ErrorMessage
from django.conf import settings


class Category(AbstractBaseModel):
    """
    Category model
    """

    name = models.CharField(help_text="Category name", unique=True, max_length=255)
    description = models.TextField(
        help_text="Category description", blank=True, null=True
    )

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class Course(AbstractBaseModel):
    """
    Course model
    """

    title = models.CharField(help_text="Course title", max_length=255, db_index=True)
    description = models.TextField(help_text="Course description")
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        help_text="Course category.",
        related_name="courses",
        null=True,
    )
    instructor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        help_text="Course Instructor.",
        related_name="courses",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    status = models.CharField(
        choices=Status.choices(),
        help_text="Status of the course.",
        max_length=8,
        default=Status.ACTIVATE.value,
    )
    image_url = models.URLField(help_text="Course image URL", blank=True, null=True)
    enrollment_limit = models.PositiveIntegerField(
        default=settings.DEFAULT_COURSE_ENROLLMENT_LIMIT
    )

    @property
    def count_enrollments(self):
        return self.enrollments.count()

    @property
    def is_full(self):
        return self.count_enrollments == self.enrollment_limit

    def __str__(self):
        return self.title


class Enrollment(AbstractBaseModel):
    """
    Enrollment model
    """

    course = models.ForeignKey(
        "courses.Course", on_delete=models.CASCADE, related_name="enrollments"
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="enrollments",
    )

    def __str__(self):
        return f"{self.student.first_name} enrolled in {self.course.title}"

    def save(self, *args, **kwargs):
        """
        Override the save method to add custom validation logic.
        """

        if self._state.adding:
            if self.course.status != Status.ACTIVATE.value:
                raise ValidationError(ErrorMessage.INACTIVE_COURSE)

            if (
                self.student
                and self.student.enrollments.filter(course=self.course).exists()
            ):
                raise ValidationError(ErrorMessage.STUDENT_ALREADY_ENROLLED)

        super().save(*args, **kwargs)
