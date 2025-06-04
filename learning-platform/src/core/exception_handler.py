from rest_framework.response import Response
from rest_framework.views import exception_handler
from core.helpers import send_capture_message
from rest_framework import status
from core.exceptions import CustomBaseException


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

    if isinstance(exception, CustomBaseException):
        return Response(
            {
                "errors": {
                    "code": exception.code,
                    "message": exception.developer_message,
                }
            },
            status=exception.status_code,
        )

    if response is not None:
        customized_response = {"errors": []}

        for key, value in response.data.items():
            error = {"field": key, "message": value}
            customized_response["errors"].append(error)

        response.data = customized_response
    else:
        send_capture_message(f"[error]{str(exception)}")
        return Response(
            data={
                "errors": {
                    "message": str(exception),
                }
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return response
