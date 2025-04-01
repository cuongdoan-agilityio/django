from superbook.celery import app


@app.task(name="post.create_post")
def sent_notification() -> float:
    """
    Sent notification
    TODO:: Need update code to sent the email.
    """

    print("Sent notification")
    return
