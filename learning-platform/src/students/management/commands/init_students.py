import random
from faker import Faker
from django.core.management.base import BaseCommand
from students.models import Student
from core.constants import ScholarshipChoices, Gender
from django.contrib.auth import get_user_model
from core.tests.utils.helpers import random_birthday, random_phone_number


User = get_user_model()
fake = Faker()


class Command(BaseCommand):
    """
    Init student command.
    """

    help = "Init student from Faker."

    def handle(self, *args, **options):
        for _ in range(50):
            student_first_name = fake.first_name()
            student_last_name = fake.last_name()
            student_email = fake.email()

            username = f"{student_first_name}.{student_last_name}"
            if (User.objects.filter(username=username).exists()) or (
                User.objects.filter(email=student_email).exists()
            ):
                return

            student_phone_number = random_phone_number()
            student_day_of_birthday = random_birthday()
            student_gender = random.choice([gender.value for gender in Gender])
            scholarship = random.choice(
                [scholarship.value for scholarship in ScholarshipChoices]
            )

            user_instance = User.objects.create_user(
                username=f"{student_first_name}.{student_last_name}",
                first_name=student_first_name,
                last_name=student_last_name,
                phone_number=student_phone_number,
                date_of_birth=student_day_of_birthday,
                gender=student_gender,
                email=student_email,
                password="Password@123",
                scholarship=scholarship,
            )

            scholarship = random.choice(
                [scholarship.value for scholarship in ScholarshipChoices]
            )
            Student.objects.create(
                user=user_instance,
                scholarship=scholarship,
            )
