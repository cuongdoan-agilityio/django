from celery import shared_task


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

    return
