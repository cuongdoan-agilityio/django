import random
from faker import Faker
from django.core.management.base import BaseCommand
from courses.models import Course
from django.contrib.auth import get_user_model
from core.constants import Status, Role
from courses.models import Enrollment

User = get_user_model()
fake = Faker()


class Command(BaseCommand):
    """
    Init enrollments command.
    """

    help = "Init Enrollments."

    def handle(self, *args, **options):
        list_students = list(User.objects.filter(role=Role.STUDENT.value).all())
        list_courses = list(Course.objects.filter(status=Status.ACTIVATE.value).all())

        if not list_students or not list_courses:
            return

        for _ in range(500):
            student = random.choice(list_students)
            course = random.choice(list_courses)

            if Enrollment.objects.filter(student=student, course=course).exists():
                continue

            Enrollment.objects.create(student=student, course=course)
