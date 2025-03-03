from core.serializers import (
    BaseBadRequestResponseSerializer,
    BaseForbiddenResponseSerializer,
    BaseSuccessResponseSerializer,
    BaseUnauthorizedResponseSerializer,
)


base_responses = {
    200: BaseSuccessResponseSerializer,
    400: BaseBadRequestResponseSerializer,
    401: BaseUnauthorizedResponseSerializer,
    403: BaseForbiddenResponseSerializer,
}
