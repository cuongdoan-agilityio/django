from celery import shared_task
import csv
from io import StringIO
import base64
from core.constants import Role
from django.contrib.auth import get_user_model
from core.helpers import send_report_email


User = get_user_model()


@shared_task
def clean_up_inactive_courses():
    """
    Deletes courses that have been inactive for more than 3 months.
    """

    return


@shared_task
def send_monthly_report():
    """
    Sends a monthly report (a CSV file sent via email) to the instructor
    about statistical number of enrolled students per their course.
    """

    instructors = User.objects.filter(role=Role.INSTRUCTOR.value)

    for instructor in instructors:
        courses = instructor.courses.all()
        csv_file = StringIO()
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(["Course Title", "Number of Enrolled"])
        for course in courses:
            student_count = course.enrollments.count()

            csv_writer.writerow([course.title, student_count])

        csv_file.seek(0)
        encoded_csv = base64.b64encode(csv_file.getvalue().encode()).decode()

        send_report_email(instructor=instructor, csv_file=encoded_csv)
