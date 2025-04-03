from superbook.celery import app
from celery.events import EventReceiver


@app.task(name="post.sent_notification")
def sent_notification() -> float:
    """
    Sent notification
    TODO:: Need update code to sent the email.
    """
    message = "Sent notification"
    return message


def post_task_monitor(app):
    def on_event(event):
        print(f"Event: {event['type']}")
        if event["type"] == "task-succeeded":
            print(f"Task {event['uuid']} Success: {event['result']}")

    with app.connection() as conn:
        recv = EventReceiver(conn, handlers={"*": on_event})
        recv.capture(limit=None, timeout=None, wakeup=True)


if __name__ == "__main__":
    post_task_monitor(app)
