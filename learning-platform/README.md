# Student Course Management System

## Overview
Develop a functional “Student Course Management System” by building, testing, and documenting REST APIs using Django Rest Framework (DRF). This phase will focus on RESTful API design and providing endpoints for the system’s mobile application (e.g., a React Native app).

## Timeline
- Estimate: 12.5 days

## Technical Stack
- Python
- Django
- Django REST Framework
- SQlite

## Code structure
    ├── src/
    │   ├── accounts
    │   │
    │   ├── categories
    │   │
    │   ├── config
    │   │
    │   ├── courses
    │   │
    │   ├── enrollments
    │   │
    │   ├── instructors
    │   │
    │   ├── students
    │
    ├── .gitignore
    ├── README.md
    ├── .env.sample.py
    ├── .env.sample
    ├── .pre-commit-config.yaml

## How to run
1. Clone the repository
```
git@gitlab.asoft-python.com:cuong.doan/django-training.git
cd learning-platform/
git checkout feat/student-course-management-system
```

2. Create a virtual environment:
Setup environments: create `.env` follow `.env.example` with your own settings

2. Create env: `uv sync` and activate it: `source .venv/bin/activate`

3. Install hook scripts: `pre-commit install`

4. Run project
    - Make migrations: `uv run ./src/manage.py makemigrations`
    - Migrate: `uv run ./src/manage.py migrate`
    - Create superuser: `uv run ./src/manage.py createsuperuser --username admin --email admin@example.com --first_name Admin --last_name User --phone_number 0937986154 --date_of_birth 1990-01-01 --gender male`
    - Run server: `uv run ./src/manage.py runserver`
