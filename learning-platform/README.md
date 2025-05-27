# Student Course Management System

## Overview
Develop a functional “Student Course Management System” by building, testing, and documenting REST APIs using Django Rest Framework (DRF). This phase will focus on RESTful API design and providing endpoints for the system’s mobile application (e.g., a React Native app).

## Timeline
- Estimate: 12.5 days
- Actual: 15.5 days
- Refactor: 5 days

## Technical Stack
- Python: 3.11.5
- Django: 5.1
- Django REST Framework: 3.15.2
- SQlite
- Ruff: 0.8.2
- UV: 0.5.29
- Drf-spectacular: 0.28.0
- Faker: 36.1.1

## Description of Requirements
- Admin Dashboard:
  - Log in to the Django admin dashboard
  - Course Management:
    - View, create, edit, delete, and filter courses
    - Perform bulk actions on courses
  - User Management:
    - View, create, edit, delete, and filter users
    - Enroll and remove students from courses
    - Set instructor to a course
  - Enrollment Management:
    - View, filter, and manage enrollments
  - Notification Management:
    - View, filter, and manage notification
- API requirement:
  - Student Management
    - Students can register, log in.
    - Students can view and update their profiles.
    - Students can see their enrolled courses (with pagination)
    - Students can enroll in or leave an active course.
    - Students can not enroll in inactive/not available courses.
    - Students can filter/search enrolled courses.
    - Email confirmation is required for registration and password reset.
    - Auto-enrollment in introduction courses for new users.
    - Send an email welcome when the student successfully registers with the system.

  - Course Management
    - Anonymous/Student can view list courses (with pagination)
    - Anonymous/Student can view course detail
    - Anonymous/Student can filter list courses by category, name, status
    - Dynamic statistics like average enrollments or top courses.

  - Instructor Management
    - Instructors can login to the system
    - Instructors can view and update their profile
    - Instructors can create or update a course
    - Instructors can view all enrolled students in their course
    - Instructors can not disable a course if it is in progress and has students enrolled in it.
    - Email confirmation is required password reset.
    - Send an email to the instructors if a course reaches enrollment limitation.

  - Notifications
    - Users (students, instructors) can see a list of notifications in their dashboard
    - Send notifications to the instructors when a student enrolls in the course
    - Send notification to students when they are removed from their enrolled course

  - Scheduling
    - Scheduling a task for weekly clean-up data (courses inactive for 3 months)
    - Scheduling a task for a monthly report (a CSV file sent via email)  sent to the instructor about the number of enrolled students per their course.

  - Performance improvements
    - Add caching (e.g., Redis, Django caching framework) for frequently accessed data
    - Implement indexing for database optimization
    - Optimize API queries using Django ORM

  - Monitoring, testing
    - Set up logging, and monitoring (e.g., Sentry)
    - Achieve >85% test coverage, focus on additional features

## Code structure
```
|   .coverage
|   .env
|   .env.example
|   .gitignore
|   .pre-commit-config.yaml
|   .python-version
|   pyproject.toml
|   README.md
|   uv.lock
|
+---documents
|       issues.md
|       improve.md
+---src
    |   .coverage
    |   db.sqlite3
    |   manage.py
    |
    +---accounts
    |   |   admin.py
    |   |   apps.py
    |   |   factories.py
    |   |   signals.py
    |   |   tasks.py
    |   |   models.py
    |   |   views.py
    |   |
    |   +---api
    |   |   |   response_schema.py
    |   |   |   serializers.py
    |   |   |   views.py
    |   |
    |   +---migrations
    |   |
    |   +---tests
    +---config
    |   |   api_router.py
    |   |   asgi.py
    |   |   urls.py
    |   |   wsgi.py
    |   |
    |   +---settings
    |   |   |   base.py
    |   |   |   local.py
    |   |   |   test.py
    |
    +---core
    |   |   api_views.py
    |   |   constants.py
    |   |   error_messages.py
    |   |   exception_handler.py
    |   |   filters.py
    |   |   helpers.py
    |   |   mixins.py
    |   |   models.py
    |   |   pagination.py
    |   |   permissions.py
    |   |   serializers.py
    |   |   validators.py
    |
    +---courses
    |   |   admin.py
    |   |   apps.py
    |   |   constants.py
    |   |   factories.py
    |   |   forms.py
    |   |   models.py
    |   |   permissions.py
    |   |   tasks.py
    |   |   signals.py
    |
    |   +---api
    |   |   |   response_schema.py
    |   |   |   serializers.py
    |   |   |   views.py
    |   |
    |   +---migrations
    |   |
    |   +---tests
    +---courses
    |   |   admin.py
    |   |   apps.py
    |   |   constants.py
    |   |   factories.py
    |   |   models.py
    |
    |   +---api
    |   |   |   response_schema.py
    |   |   |   serializers.py
    |   |   |   views.py
    |   |
    |   +---migrations
    |   |
    |   +---tests
```

## How to run
1. Clone the repository
```
git@gitlab.asoft-python.com:cuong.doan/django-training.git
git checkout feat/student-course-management-system
cd learning-platform/
```

2. Create a virtual environment:
Setup environments: create `.env` follow `.env.example` with your own settings

3. Create env: `uv sync` and activate it: `source .venv/bin/activate`
4. Check Redis server:
`redis-cli ping`: if result is not `PONG` we need run redis server

5. Install hook scripts: `pre-commit install`

6. Run project
- Make migrations: `uv run ./src/manage.py makemigrations`
- Migrate: `uv run ./src/manage.py migrate`
- Create superuser: `uv run ./src/manage.py createsuperuser --username admin --email admin@example.com`
- Run server: `uv run ./src/manage.py runserver`
- Run Celery:
  - cd to `src` folder.
  - `celery -A config worker --pool=solo --loglevel=info`
  - `celery -A config beat --loglevel=info`
- Swagger documents: `http://127.0.0.1:8000/docs/swagger/`
- Admin page: `http://127.0.0.1:8000/admin-dashboard/`
7. Init data
- Init instructors and courses data: `uv run ./src/manage.py init_courses`
- Init students data: `uv run ./src/manage.py init_students`
- Init enrollments data: `uv run ./src/manage.py init_enrollments`

1. Flow create data with admin page
- Login to [admin page](http://127.0.0.1:8000/admin-dashboard/) with admin info.
- Create course specializations.
- Create students.
- Create instructors.
- Create courses with specialization and instructor.
- Create Enrollments.

## Unit Testing
- pytest --cov=src --cov-report html

## APIs
### Auth
  - Login:
    - POST: /api/v1/auth/login/
  - Signup:
    - POST: /api/v1/auth/signup/
  - Confirm Signup Email
    - POST: /api/v1/auth/confirm-signup-email
  - Reset Password
    - POST: /api/v1/auth/reset-password/
  - Confirm Reset Password
    - POST: /api/v1/auth/confirm-reset-password/

###  User
  - Get profile
    - GET: /api/v1/users/{id}/
    - GET: /api/v1/users/me/
  - Update profile
    - PATCH: /api/v1/users/{id}/

### Category
  - Get category
    - GET: /api/v1/categories/

### Specialization
  - Get specialization
    - GET: /api/v1/specializations/

### Courses
  - Get courses
    - GET: /api/v1/courses/
  - Create courses
    - POST: /api/v1/courses/
  - Get course detail
    - GET: /api/v1/courses/{id}/
  - Update course
    - PATCH: /api/v1/courses/{id}/
  - Enroll course
    - POST: /api/v1/courses/{id}/enroll/
  - Leave course
    - POST: /api/v1/courses/{id}/leave/
  - Get course student
    - GET: /api/v1/courses/{id}/students/
  - Get top courses
    - GET: /api/v1/courses/top/

### Notifications
  - Get notifications
    - GET: /api/v1/notifications/
  - Get notification detail
    - GET: /api/v1/notifications/{id}/
  - Update notification
    - PATCH: /api/v1/notifications/{id}

## Issues
- [Issues document](./documents/issues.md)
