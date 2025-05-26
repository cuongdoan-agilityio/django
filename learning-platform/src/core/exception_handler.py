from rest_framework.response import Response
from rest_framework.views import exception_handler


def process_exception(exception, context) -> Response:
    """
    Process the exception

    Args:
        exception (Exception): The exception
        context (dict): the context

    Returns:
        Response: Response
    """
    response = exception_handler(exception, context)

    # Update the structure of the response data.
    # Thanh Nguyen: must check 500 error
    # Minh Tran: When making a feature, you should research around it.
    # Minh Tran: With the feature verify signup email, verify reset password email, you need to create a django view, when the user clicks the link, it will lead to that view instead of the APIs view.

    if response is not None:
        customized_response = {"errors": []}

        for key, value in response.data.items():
            error = {"field": key, "message": value}
            customized_response["errors"].append(error)

        response.data = customized_response

    return response
