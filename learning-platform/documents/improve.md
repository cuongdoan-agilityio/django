# Improve

- Use other database management systems instead of `SQLite`.
- `Subject` and `Category` models should have `many-to-many` relationships with each other.
- Need docker integration.
- Handle exceptions before requests are sent to views, with [Middleware](https://docs.djangoproject.com/en/5.1/topics/http/middleware/)
- Check again if the two models `Student` and `Instructor` are necessary
- Change the model pk to `ID`, [MR link](https://gitlab.asoft-python.com/cuong.doan/django-training/-/merge_requests/14)
- Apply django [signals](https://docs.djangoproject.com/en/5.1/topics/signals/)
- Model Validation
  - Should use Django password validation rules then extend only if not meet your requirements. [Ref](https://docs.djangoproject.com/en/5.1/topics/auth/passwords/#module-django.contrib.auth.password_validation)
  - Should write custom validator instead of separate function to validate (use both in form and model fields). [Ref](https://docs.djangoproject.com/en/5.1/topics/auth/passwords/#writing-your-own-validator)
