import csv
import base64
import logging
from io import StringIO
from datetime import datetime

from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count
from dateutil.relativedelta import relativedelta
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
def report_to_instructor(self, instructor_id):
    """
    Sends a monthly report (a CSV file sent via email) to the instructor.
    """

    try:
        instructor = User.objects.filter(id=instructor_id).first()

        if not instructor:
            logging.error("No instructor found")
            raise ObjectDoesNotExist(
                f"Instructor with ID {instructor_id} does not exist."
            )

        courses = instructor.courses.prefetch_related("enrollments").annotate(
            enrollment_count=Count("enrollments")
        )
        if not courses:
            return

        # TODO: should move logic create CSV to service.
        csv_file = StringIO()
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(["Course Title", "Number of Enrolled"])
        for course in courses:
            csv_writer.writerow([course.title, course.enrollment_count])

        csv_file.seek(0)
        encoded_csv = base64.b64encode(csv_file.getvalue().encode()).decode()

        send_report_email(instructor=instructor, csv_file=encoded_csv)

    except Exception as exc:
        logger.error(
            f"Failed to process email for instructor {instructor.id}: {str(exc)}"
        )
        raise self.retry(exc=exc)


@shared_task
def send_monthly_report():
    """
    Sends a monthly report (a CSV file sent via email) to the instructor
    about statistical number of enrolled students per their course.
    """

    tasks = []
    instructors = User.objects.filter(role=Role.INSTRUCTOR.value)
    if instructors.exists() is False:
        return

    try:
        for instructor in instructors:
            tasks.append(report_to_instructor.s(instructor.id))

        # Minh tran: check task finish/ false
        if tasks:
            job = group(tasks)
            job.apply_async()

    except Exception as exc:
        logger.error(f"Unexpected error in send_monthly_report: {str(exc)}")
        raise
