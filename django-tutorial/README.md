# Django Tutorial
> Project setup follow [Django tutorial](https://docs.djangoproject.com/en/5.1/intro/tutorial01/)

### Environment
- [uv](https://docs.astral.sh/uv): python package manager

## Run this project
1. Create env: `uv venv`
2. Install: `uv pip install -r pyproject.yml`

## Extensions:
- [SQLite Viewer](https://marketplace.visualstudio.com/items?itemName=qwtel.sqlite-viewer) - help view db sqlite in VSCode

## Step init this project
1. Init python project `uv init django-tutorial`
2. Add package Django `uv add django`
3. Add first Django project: `uv run django-admin startproject mysite django-tutorial` (stand in `boilerplate` folder)
4. Run project `python manage.py runserver` (stand in `django-tutorial` folder) --> access http://127.0.0.1:8000/ to see app
5. Start first app in Django project `uv run python manage.py startapp polls`
6. Add some code for views and urls -> http://127.0.0.1:8000/polls/
7. Migrate INSTALLED_APPS default add by Django `uv run python manage.py migrate` --> Checkout the database and see its tables create (auth_user, etc.) in db via SQLite Viewer
8. Add model, add poll app -> Make migrations file (new file add in migrations) and migrate to database (new table add in db)
9. Play around with Django shell
10. Add super user `uv run python manage.py createsuperuser` -> run app again and access admin dashboard
...
