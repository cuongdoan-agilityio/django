class FormatDataMixin:
    """
    Format the response data.
    """

    def format_data(self, instance, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(instance, *args, **kwargs)
        data = serializer.data
        return {"data": {**data}}
