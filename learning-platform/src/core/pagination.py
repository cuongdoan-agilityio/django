from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class CustomPagination(PageNumberPagination):
    """
    Custom pagination class to include pagination metadata in the response.

    Methods:
        get_paginated_response: Returns a paginated response with metadata.
    """

    page_size = 10
    page_size_query_param = "page_size"
    page_query_param = "page_number"

    def get_paginated_response(self, data):
        return Response(
            {
                "data": data,
                "meta": {
                    "pagination": {
                        "total": self.page.paginator.count,
                        "page_size": self.get_page_size(self.request),
                        "page_number": self.page.start_index(),
                    }
                },
            }
        )
