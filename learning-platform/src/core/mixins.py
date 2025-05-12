from rest_framework.response import Response


class FormatDataMixin:
    """
    Format the response data.
    """

    def format_data(self, instance, *args, **kwargs):
        """
        Format the response data.
        """
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(instance, *args, **kwargs)
        data = serializer.data
        return {"data": {**data}}

    def format_list_data(self, data, *args, **kwargs):
        """
        Format the response data for list view.
        """

        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data, many=True, *args, **kwargs)
        data = serializer.data
        return {"data": data}


class CustomRetrieveModelMixin:
    """
    Custom retrieve a model instance.
    """

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = serializer.data

        return Response(
            {
                "data": {**data},
            }
        )
