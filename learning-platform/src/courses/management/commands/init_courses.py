from django.core.management.base import BaseCommand
from courses.models import Course, Category
from instructors.models import Instructor, Subject
from core.constants import Degree, Status, Gender
from django.contrib.auth import get_user_model
from faker import Faker
import random
from datetime import date, timedelta


User = get_user_model()
fake = Faker()


class Command(BaseCommand):
    """
    Init courses command.
    """

    help = "Init courses, instructors, categories and subjects using Faker."

    def handle(self, *args, **options):
        for _ in range(50):
            category_name = fake.word()
            category_description = fake.paragraph(nb_sentences=1)
            subject_description = fake.paragraph(nb_sentences=1)

            instructor_first_name = fake.first_name()
            instructor_last_name = fake.last_name()
            instructor_email = fake.email()
            instructor_phone_number = self.random_phone_number()
            instructor_day_of_birthday = self.random_birthday()
            instructor_gender = random.choice([gender.value for gender in Gender])

            category, _ = Category.objects.get_or_create(
                name=category_name, defaults={"description": category_description}
            )

            subject, _ = Subject.objects.get_or_create(
                name=category_name, defaults={"description": subject_description}
            )

            user_instance = User.objects.create_user(
                username=f"{instructor_first_name}.{instructor_last_name}",
                first_name=instructor_first_name,
                last_name=instructor_last_name,
                phone_number=instructor_phone_number,
                date_of_birth=instructor_day_of_birthday,
                gender=instructor_gender,
                email=instructor_email,
                password="Password@123",
            )

            degree = random.choice([degree.value for degree in Degree])
            instructor_instance = Instructor.objects.create(
                user=user_instance,
                degree=degree,
            )
            instructor_instance.subjects.set([str(subject.uuid)])

            status = random.choice([status.value for status in Status])
            Course.objects.create(
                category=category,
                instructor=instructor_instance,
                title=fake.sentence(nb_words=6),
                description=fake.paragraph(nb_sentences=3),
                status=status,
                image=fake.image_url(),
            )

    def random_birthday(self):
        """
        Generate a random date of birth between 6 and 100 years ago.

        Returns:
            date: A random date of birth.
        """

        today = date.today()
        min_years_ago = today - timedelta(days=6 * 365)
        max_years_ago = today - timedelta(days=100 * 365)

        start_date = max_years_ago
        end_date = min_years_ago

        return fake.date_between_dates(date_start=start_date, date_end=end_date)

    def random_phone_number(self):
        """
        Generate a random phone number with a length between 10 and 11 digits.

        Returns:
            str: A random phone number.
        """

        length = random.randint(10, 11)
        phone_number = "".join([str(random.randint(0, 9)) for _ in range(length)])
        return phone_number
