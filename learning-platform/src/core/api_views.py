from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet, GenericViewSet


class CommonViewSet:
    """
    Common view set for all view sets
    - create response
    - get resource URI
    """

    def ok(self, data: dict | None = None) -> Response:
        """
        Default response ok. Status code is 200
        """
        if not data:
            data = {"success": True}

        return Response(data=data, status=status.HTTP_200_OK)

    def created(self, data: dict | None = None) -> Response:
        """
        Default response created. Status code is 201
        """
        if not data:
            data = {"success": True}

        return Response(data=data, status=status.HTTP_201_CREATED)

    def forbidden(self, data: dict | None = None) -> Response:
        """
        Default response forbidden. Status code is 403
        """
        if not data:
            data = {
                "errors": {
                    "field": "detail",
                    "message": "You do not have permission to perform this action.",
                },
            }

        return Response(data=data, status=status.HTTP_403_FORBIDDEN)

    def bad_request(self, message=None, field=None):
        """
        Return bad request with message content & code
        """
        # Build up the error content.
        response_data = {
            "errors": {
                "field": field,
                "message": [message],
            },
        }

        return Response(data=response_data, status=status.HTTP_400_BAD_REQUEST)

    def unauthorized_request(self, field=None, message=None):
        """
        Return unauthorized request with message content
        """
        # Build up the error content.
        response_data = {
            "errors": {
                "field": field,
                "message": message,
            },
        }

        return Response(data=response_data, status=status.HTTP_401_UNAUTHORIZED)

    def not_found(self, field="detail", message="Not found"):
        """
        Return not found request with message content
        """
        # Build up the error content.
        response_data = {
            "errors": {
                "field": field,
                "message": message,
            }
        }

        return Response(data=response_data, status=status.HTTP_404_NOT_FOUND)

    def finalize_response(self, request, response, *args, **kwargs):
        """
        Finalize the response structure for API responses.
        """

        data = response.data
        if (
            isinstance(response, Response)
            and ("data" not in data)
            and ("errors" not in data)
        ):
            if isinstance(response.data, dict):
                response.data = {
                    "data": response.data,
                }

        return super().finalize_response(request, response, *args, **kwargs)

    def internal_server_error(
        self,
        field=None,
        message="An unexpected error occurred. Please try again later.",
    ):
        """
        Return internal server error response with message content.
        """

        response_data = {
            "errors": {
                "field": field,
                "message": message,
            },
        }

        return Response(
            data=response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class BaseViewSet(CommonViewSet, ViewSet):
    """
    Base view set for views accept DTO data rather than Django model
    """


class BaseGenericViewSet(CommonViewSet, GenericViewSet):
    """
    Base generic view set.
    """
