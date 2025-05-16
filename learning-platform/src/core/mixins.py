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
        Format the response of list data.
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


class CustomUpdateModelMixin:
    """
    Custom update a model instance.
    """

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, "_prefetched_objects_cache", None):
            instance._prefetched_objects_cache = {}

        data = serializer.data
        response_data = {"data": {**data}}
        return Response(response_data)
