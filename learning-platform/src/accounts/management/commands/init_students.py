import random
from faker import Faker
from django.core.management.base import BaseCommand
from django.db.models.signals import post_save
from django.contrib.auth import get_user_model
from accounts.signals import send_verify_email, enroll_intro_course
from core.constants import ScholarshipChoices, Gender, Role
from core.tests.utils.helpers import random_birthday, random_phone_number


User = get_user_model()
fake = Faker()


class Command(BaseCommand):
    """
    Init student command.
    """

    help = "Init student from Faker."

    def handle(self, *args, **options):
        # Disconnect the signal.
        post_save.disconnect(receiver=send_verify_email, sender=User)
        post_save.disconnect(receiver=enroll_intro_course, sender=User)

        for _ in range(500):
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

            User.objects.create_user(
                username=f"{student_first_name}.{student_last_name}",
                first_name=student_first_name,
                last_name=student_last_name,
                phone_number=student_phone_number,
                date_of_birth=student_day_of_birthday,
                gender=student_gender,
                email=student_email,
                password="Password@123",
                scholarship=scholarship,
                role=Role.STUDENT.value,
            )

        # Connect the signal.
        post_save.connect(receiver=send_verify_email, sender=User)
        post_save.connect(receiver=enroll_intro_course, sender=User)
