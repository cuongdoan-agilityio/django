from rest_framework.mixins import ListModelMixin
from rest_framework.permissions import AllowAny

from core.api_views import BaseGenericViewSet
from accounts.models import Subject

from .serializers import SubjectSerializer


class SubjectViewSet(BaseGenericViewSet, ListModelMixin):
    """
    Subject view set
    """

    permission_classes = [AllowAny]
    serializer_class = SubjectSerializer
    http_method_names = ["get"]
    resource_name = "subjects"

    def get_queryset(self):
        return Subject.objects.all()


apps = [SubjectViewSet]
