import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("courses", "0005_category"),
    ]

    operations = [
        migrations.AlterField(
            model_name="course",
            name="category",
            field=models.ForeignKey(
                help_text="Course category.",
                on_delete=django.db.models.deletion.CASCADE,
                related_name="courses",
                to="courses.category",
            ),
        ),
    ]
