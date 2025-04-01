from celery import Celery


app = Celery("superbook")

app.conf.update(
    result_expires=3600,
)

if __name__ == "__main__":
    app.start()
