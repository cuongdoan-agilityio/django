from rest_framework.response import Response


class CustomListModelMixin:
    """
    List a queryset.
    """

    def list(self, request, *args, **kwargs):
        """
        List a queryset with optional pagination.

        This method retrieves a filtered queryset, applies pagination if necessary,
        and formats the response data to include metadata for paginated results.
        """
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            pagination_data = self.get_paginated_response(page)
            data = pagination_data.data
            serializer = self.get_serializer(
                {
                    "data": data.get("data"),
                    "meta": data.get("meta"),
                }
            )
            return Response(serializer.data)

        serializer = self.get_serializer({"data": queryset})
        return Response(serializer.data)


class CustomRetrieveModelMixin:
    """
    Custom retrieve a model instance.
    """

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer({"data": instance})
        return Response(serializer.data)
