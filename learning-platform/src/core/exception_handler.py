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
    if response is not None:
        customized_response = {"errors": []}

        for key, value in response.data.items():
            error = {"field": key, "message": value}
            customized_response["errors"].append(error)

        response.data = customized_response

    return response
