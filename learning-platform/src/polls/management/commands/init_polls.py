import os
import json
from django.core.management.base import BaseCommand
from django.utils import timezone
from polls.models import Poll, Question, Choice


class Command(BaseCommand):
    """
    Init polls command
    """

    help = "Populate polls with questions and choices from a JSON file"

    def handle(self, *args, **options):
        self.stdout.write("Start populated polls with questions and choices...")

        file_path = os.path.join(os.path.dirname(__file__), "polls.json")

        # Load JSON data
        with open(file_path, "r") as file:
            data = json.load(file)

        # Iterate through the questions and create Question and Choice objects
        for item in data:
            questions = item["questions"]

            # Create a Poll object
            poll = Poll.objects.create(
                name=item["name"], description=item["description"]
            )

            for question_dict in questions:
                # Create a Question object
                question = Question.objects.create(
                    poll=poll,
                    question_text=question_dict["question_text"],
                    pub_date=timezone.now(),
                )

                # Create Choice objects for the question
                for choice_text in question_dict["choices"]:
                    Choice.objects.create(
                        question=question, choice_text=choice_text, votes=0
                    )

        self.stdout.write("Successfully populated questions and choices.")
