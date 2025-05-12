from os import environ

from split_settings.tools import include


environ.setdefault("DJANGO_ENV", "local")
ENV = environ["DJANGO_ENV"]

include(
    f"{ENV}.py",
)
