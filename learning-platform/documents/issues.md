# Practice issues

- Use `SQLite` instead of other database management systems.
  - Solution: Should use `PostgreSQL`, `MySQL`, ...

- `Subject` and `Category` models should have `many-to-many` relationships with each other.

- Haven't created constants to manage messages.

- Haven't used docker yet
  - Need docker integration.

- Didn't understand the requirements at the beginning: Working on course management at school, actually online course.
  - Consequences, slow progress

- For `pagination` feature, need validation pagination information, if page number not found, return empty data instead of page does not exist error.

- Need to handle response data for failed API calls.

- Handle API documentation not displaying correct structure in Swagger.
  - References: [How to generate a schema for a custom pagination in django rfw with drf-spectacular?](https://stackoverflow.com/questions/71431687/how-to-generate-a-schema-for-a-custom-pagination-in-django-rfw-with-drf-spectacu)
  - [DRF pagination.py](https://github.com/encode/django-rest-framework/blob/master/rest_framework/pagination.py)

- Check the `role` field in `User` mode, is this field really necessary?

- Check again if the two models `Student` and `Instructor` are necessary, and the problems caused:
  - The 1-1 relationship between the two models above with the `User` model makes it difficult to create documents and create APIs.
  - Requires more serializers and needs to customize the data structure returned to the user.
  - Takes a lot of time to do.
