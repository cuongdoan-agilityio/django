import django_extensions.db.fields
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("courses", "0004_alter_course_description"),
    ]

    operations = [
        migrations.CreateModel(
            name="Category",
            fields=[
                (
                    "created",
                    django_extensions.db.fields.CreationDateTimeField(
                        auto_now_add=True, verbose_name="created"
                    ),
                ),
                (
                    "modified",
                    django_extensions.db.fields.ModificationDateTimeField(
                        auto_now=True, verbose_name="modified"
                    ),
                ),
                (
                    "uuid",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                        unique=True,
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        help_text="Category name", max_length=255, unique=True
                    ),
                ),
                (
                    "description",
                    models.TextField(
                        blank=True, help_text="Category description", null=True
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
    ]
