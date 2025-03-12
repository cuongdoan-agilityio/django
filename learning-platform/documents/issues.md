# Practice issues

- Use `SQLite` instead of other database management systems.
  - Solution: Should use `PostgreSQL`, `MySQL`, ...

- `Subject` and `Category` models should have `many-to-many` relationships with each other.

- Haven't used docker yet
  - Need docker integration.

- Didn't understand the requirements at the beginning: Working on course management at school, actually online course.
  - Consequences, slow progress

- Need to handle response data for failed API calls.
  - Handle exceptions before requests are sent to views, Use [Middleware](https://docs.djangoproject.com/en/5.1/topics/http/middleware/) to customize
  - Handle exception requests when sent to views: [Custom exception handling](https://www.django-rest-framework.org/api-guide/exceptions/#custom-exception-handling)

- Handle API documentation not displaying correct structure in Swagger.
  - References: [How to generate a schema for a custom pagination in django rfw with drf-spectacular?](https://stackoverflow.com/questions/71431687/how-to-generate-a-schema-for-a-custom-pagination-in-django-rfw-with-drf-spectacu)
  - [DRF pagination.py](https://github.com/encode/django-rest-framework/blob/master/rest_framework/pagination.py)

- Check the `role` field in `User` mode, is this field really necessary?

- Check again if the two models `Student` and `Instructor` are necessary, and the problems caused:
  - The 1-1 relationship between the two models above with the `User` model makes it difficult to create documents and create APIs.
  - Requires more serializers and needs to customize the data structure returned to the user.
  - Takes a lot of time to do.
  - Change the model pk to `ID`, [MR link](https://gitlab.asoft-python.com/cuong.doan/django-training/-/merge_requests/14)
