import os
import json
from django.core.management.base import BaseCommand
from students.models import Student
from core.constants import ScholarshipChoices
from django.contrib.auth import get_user_model


User = get_user_model()


class Command(BaseCommand):
    """
    Init student command.
    """

    help = "Init student from JSON file."

    def handle(self, *args, **options):
        file_path = os.path.join(os.path.dirname(__file__), "students.json")

        # Load JSON data
        with open(file_path, "r") as file:
            data = json.load(file)

        for item in data:
            first_name = item["first_name"]
            last_name = item["last_name"]
            email = item["email"]

            user_instance = User.objects.create_user(
                username=f"{first_name}.{last_name}",
                email=email,
                password="Password@123",
            )
            Student.objects.get_or_create(
                user=user_instance,
                scholarship=ScholarshipChoices.ZERO.value,
            )
