# Django Practice Boilerplate
This is a boilerplate for Django practice, providing a basic setup for Django project with pre-commit hooks.

### Techstack
- Python
- Django
- Django Rest Framework
- SQLite

### Prerequisites
Install the following tools to your machine:
- [uv](https://docs.astral.sh/uv): python package manager
- [pre-commit](https://pre-commit.com/): framework for managing and maintaining multi-language pre-commit hooks

## Run this project
0. Stand in `django-practice` directory
1. Setup environments: create `.env` follow `.env.example` with your own settings
2. Create env: `uv venv` and activate it: `source .venv/bin/activate`
3. Install packages: `uv sync`
   - Install all packages: `uv sync`
   - Install except dev packages: `uv sync --no-group dev`
4. Install hook scripts: `pre-commit install`
5. Run project:
    - Migrate: `uv run ./src/manage.py migrate`
    - Init data: `uv run ./src/manage.py init_polls`
    - Run server: `uv run ./src/manage.py runserver`
    - Go http://localhost:8000/polls/ to see the page (app)
    - Go http://localhost:8000/api/v1/polls/ to see list poll questions (api)

## Boilerplate Information
- Use [uv](https://docs.astral.sh/uv) for python package manager
- Use [pre-commit](https://pre-commit.com/) for managing and maintaining multi-language pre-commit hooks
- Use [SQLite](https://www.sqlite.org/index.html) for database by default
- Use [django-environ](https://github.com/joke2k/django-environ) for environment variables
- Hooks applied:
  - [pre-commit-hooks](https://github.com/pre-commit/pre-commit-hooks) - basic hooks
  - [ruff-pre-commit](https://github.com/astral-sh/ruff-pre-commit)
  - [djLint](https://github.com/Riverside-Healthcare/djLint) - HTML Template Linter and Formatter for Django

## Commands:
### uv
- Add package
  - Add to project: `uv add <package-name>`
  - Add to `dev` group: `uv add --dev <dev-package-name>`
- Install packages:
   - Install all packages: `uv sync`
   - Install except dev packages: `uv sync --no-group dev`
- Run command in virtual environment: `uv run <command>`
- Ruff check: `ruff check`

### pre-commit
- Install hook scripts: `pre-commit install`
- Run pre-commit: `pre-commit run --all-files`
