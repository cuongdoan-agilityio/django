import csv
import base64
import logging
from io import StringIO
from datetime import datetime

from django.contrib.auth import get_user_model
from dateutil.relativedelta import relativedelta
from django.db.models import Count
from celery import shared_task, group

from core.constants import Role, Status
from core.helpers import send_report_email
from courses.models import Course


User = get_user_model()
logger = logging.getLogger(__name__)


@shared_task
def clean_up_inactive_courses():
    """
    Deletes courses that have been inactive for more than 3 months.
    """

    delta_time = datetime.now() - relativedelta(months=3)
    # Don't delete system courses
    Course.objects.filter(
        instructor__isnull=False, status=Status.INACTIVE.value, modified__lt=delta_time
    ).delete()


@shared_task(bind=True, max_retries=2, default_retry_delay=60)
def report_to_instructor(self, instructor, courses):
    """
    Sends a monthly report (a CSV file sent via email) to the instructor.
    """

    try:
        # TODO: should move logic create CSV to service.
        csv_file = StringIO()
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(["Course Title", "Number of Enrolled"])
        for course in courses:
            csv_writer.writerow([course.get("title"), course.get("enrollment_count")])

        csv_file.seek(0)
        encoded_csv = base64.b64encode(csv_file.getvalue().encode()).decode()

        send_report_email(instructor=instructor, csv_file=encoded_csv)

    except Exception as exc:
        logger.error(
            f"Failed to process email for instructor {instructor.get('id')}: {str(exc)}"
        )
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=2, default_retry_delay=60)
def send_monthly_report(self):
    """
    Sends a monthly report (a CSV file sent via email) to the instructor
    about statistical number of enrolled students per their course.
    """

    instructors = User.objects.filter(role=Role.INSTRUCTOR.value).prefetch_related(
        "courses__enrollments"
    )
    tasks = []
    try:
        for instructor in instructors:
            courses = instructor.courses.annotate(enrollment_count=Count("enrollments"))
            if not courses:
                continue

            instructor_data = {
                "id": instructor.id,
                "email": instructor.email,
                "username": instructor.username,
            }
            courses_data = [
                {"title": course.title, "enrollment_count": course.enrollment_count}
                for course in courses
            ]
            tasks.append(
                report_to_instructor.s(
                    instructor=instructor_data,
                    courses=courses_data,
                )
            )

        if tasks:
            job = group(tasks)
            job.apply_async()

    except Exception as exc:
        raise self.retry(exc=exc)
