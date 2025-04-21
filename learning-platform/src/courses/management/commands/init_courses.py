import random
from faker import Faker
from django.core.management.base import BaseCommand
from courses.models import Course, Category
from accounts.models import Subject
from core.constants import Degree, Status, Gender, Role
from django.contrib.auth import get_user_model
from core.tests.utils.helpers import random_birthday, random_phone_number


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

            username = f"{instructor_first_name}.{instructor_last_name}"
            if (User.objects.filter(username=username).exists()) or (
                User.objects.filter(email=instructor_email).exists()
            ):
                return

            instructor_phone_number = random_phone_number()
            instructor_day_of_birthday = random_birthday()
            instructor_gender = random.choice([gender.value for gender in Gender])
            category, _ = Category.objects.get_or_create(
                name=category_name, defaults={"description": category_description}
            )
            subject, _ = Subject.objects.get_or_create(
                name=category_name, defaults={"description": subject_description}
            )
            degree = random.choice([degree.value for degree in Degree])

            user_instance = User.objects.create_user(
                username=username,
                first_name=instructor_first_name,
                last_name=instructor_last_name,
                phone_number=instructor_phone_number,
                date_of_birth=instructor_day_of_birthday,
                gender=instructor_gender,
                email=instructor_email,
                password="Password@123",
                degree=degree,
                role=Role.INSTRUCTOR.value,
            )
            user_instance.subjects.set([str(subject.id)])

            status = random.choice([status.value for status in Status])
            Course.objects.create(
                category=category,
                instructor=user_instance,
                title=fake.sentence(nb_words=6),
                description=fake.paragraph(nb_sentences=3),
                status=status,
                image_url=fake.image_url(),
            )
