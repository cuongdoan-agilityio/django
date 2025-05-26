class FormatDataMixin:
    """
    Format the response data.
    """

    def format_data(self, instance, *args, **kwargs):  # Minh Tran: rename
        """
        Format the response data.
        """
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(instance, *args, **kwargs)
        data = serializer.data
        return data

    def format_list_data(self, data, *args, **kwargs):
        """
        Format the response of list data.
        """

        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data, many=True, *args, **kwargs)
        data = serializer.data
        return {"data": data}
