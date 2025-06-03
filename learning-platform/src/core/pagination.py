from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response


class CustomPagination(LimitOffsetPagination):
    """
    Custom pagination class to include pagination metadata in the response.
    """

    def get_paginated_response(self, data):
        return Response(
            {
                "data": data,
                "meta": {
                    "pagination": {
                        "total": self.count,
                        "limit": self.limit,
                        "offset": self.offset,
                    }
                },
            }
        )

    # TODO: Need refactor
    # def get_paginated_response_schema(self, schema):
    #     return {
    #         "type": "object",
    #         "properties": {
    #             "data": schema.data,
    #             "meta": {
    #                 "type": "object",
    #                 "properties": {
    #                     "pagination": {
    #                         "type": "object",
    #                         "properties": {
    #                             "total": {
    #                                 "type": "integer",
    #                                 "example": 1,
    #                             },
    #                             "limit": {
    #                                 "type": "integer",
    #                                 "example": 20,
    #                             },
    #                             "offset": {
    #                                 "type": "integer",
    #                                 "example": 0,
    #                             },
    #                         },
    #                     },
    #                 },
    #             },
    #         },
    #     }
