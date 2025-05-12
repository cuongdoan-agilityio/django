"""
Copyright © 2022-present Agility IO, LLC. All rights reserved.

The contents of this file are subject to the terms of the End User License
Agreement (EULA) and Enterprise Services Agreement (ESA) agreed upon between
You and Agility IO, LLC, collectively (“License”).
You may not use this file except in compliance with the License. You can obtain
a copy of the License by contacting Agility IO, LLC.
See the License for the specific language governing permissions and limitations
under the License including but not limited to modification and distribution
rights of the Software.
"""

import traceback

from rest_framework.response import Response
from rest_framework.views import exception_handler


def is_registered(exception) -> bool:
    """
    Check if exception is registered.

    Returns:
        bool: True if the exception is registered, False otherwise.
    """
    try:
        return exception.is_an_error_response
    except AttributeError:
        # TODO: need send error to sentry
        pass

        return False


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
    if is_registered(exception):
        status = exception.status_code
        exception_dict = exception.to_dict()
        traceback.print_exc()
        return Response(data=exception_dict, status=status)

    # Update the structure of the response data.
    if response is not None:
        customized_response = {"errors": []}

        for key, value in response.data.items():
            error = {"field": key, "message": value}
            customized_response["errors"].append(error)

        response.data = customized_response

    return response
