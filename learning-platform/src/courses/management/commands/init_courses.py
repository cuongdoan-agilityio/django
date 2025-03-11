import os
import json
from django.core.management.base import BaseCommand
from courses.models import Course
from categories.models import Category
from instructors.models import Instructor, Subject
from core.constants import Degree
from django.contrib.auth import get_user_model


User = get_user_model()


class Command(BaseCommand):
    """
    Init courses command.
    """

    help = "Init courses, instructors, categories and subjects from JSON file."

    def handle(self, *args, **options):
        file_path = os.path.join(os.path.dirname(__file__), "courses.json")

        # Load JSON data
        with open(file_path, "r") as file:
            data = json.load(file)

        for item in data:
            category_name = item["category"]["name"]
            instructor = item["instructor"]

            category, _ = Category.objects.get_or_create(name=category_name)
            subject, _ = Subject.objects.get_or_create(name=category_name)

            user_instance = User.objects.create_user(
                username=f"{instructor['first_name']}.{instructor['last_name']}",
                email=instructor["email"],
                password="Password@123",
            )
            instructor_instance = Instructor.objects.create(
                user=user_instance,
                degree=Degree.MASTER.value,
            )
            print()
            instructor_instance.subjects.set([str(subject.uuid)])

            Course.objects.create(
                category=category,
                instructor=instructor_instance,
                title=item["title"],
                description=item["description"],
                status=item["status"],
            )
