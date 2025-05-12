class FormatDataMixin:
    """
    Format the response data.
    """

    def format_data(self, instance, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        kwargs["context"] = self.get_serializer_context()
        serializer = serializer_class(instance, *args, **kwargs)
        data = serializer.data
        return {"data": {**data}}
