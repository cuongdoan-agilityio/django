from rest_framework import serializers


class DataSuccessSerializer(serializers.Serializer):
    """
    Serializer for indicating a successful response.

    Fields:
        success (BooleanField): Indicates whether the operation was successful.
    """

    success = serializers.BooleanField(default=True)


class ErrorSerializer(serializers.Serializer):
    """
    Serializer for representing an error.

    Fields:
        field (CharField): The field where the error occurred.
        message (CharField): The error message.
    """

    field = serializers.CharField(help_text="The error field")
    message = serializers.CharField(help_text="Default error message.")


class BadRequestSerializer(serializers.Serializer):
    """
    Serializer for representing a bad request error.

    Fields:
        message (CharField): A user-friendly error message.
    """

    developerMessage = serializers.CharField(help_text="User friendly message")
    message = serializers.ListField(help_text="User friendly message")
    code = serializers.CharField(help_text="Code")


class BaseSuccessResponseSerializer(serializers.Serializer):
    """
    Base serializer for a successful response.

    Fields:
        data (DataSuccessSerializer): The data indicating success.
    """

    data = DataSuccessSerializer()


class BaseBadRequestResponseSerializer(serializers.Serializer):
    """
    Base serializer for a bad request response.

    Fields:
        errors (BadRequestSerializer): The errors indicating the bad request.
    """

    errors = BadRequestSerializer()


class BaseUnauthorizedResponseSerializer(serializers.Serializer):
    """
    Base serializer for an unauthorized response.

    Fields:
        errors (ErrorSerializer): The errors indicating the unauthorized request.
    """

    errors = ErrorSerializer(many=True)


class BaseForbiddenResponseSerializer(serializers.Serializer):
    """
    Base serializer for a forbidden response.

    Fields:
        detail (CharField): The errors indicating the forbidden request.
    """

    detail = serializers.CharField(help_text="User friendly message")


class PaginationSerializer(serializers.Serializer):
    """
    Serializer for pagination.
    """

    total = serializers.IntegerField()
    page_size = serializers.IntegerField()
    page_number = serializers.IntegerField()

    def to_representation(self, instance):
        return {
            "total": instance.total,
            "page_size": instance.page_size,
            "page_number": instance.page_number,
        }


class MetaSerializer(serializers.Serializer):
    """
    Serializer for meta data.
    """

    pagination = PaginationSerializer()
