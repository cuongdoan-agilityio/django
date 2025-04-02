from superbook.celery import app


@app.task(name="post.sent_notification")
def sent_notification() -> float:
    """
    Sent notification
    TODO:: Need update code to sent the email.
    """
    message = "Sent notification"
    return message
