from celery import Celery
import os


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "superbook.settings")

app = Celery("superbook")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

if __name__ == "__main__":
    app.start()
