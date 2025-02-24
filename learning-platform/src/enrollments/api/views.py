from rest_framework.permissions import AllowAny

from core.api_views import BaseModelViewSet
from ..models import Enrollment
from .serializers import EnrollmentSerializer


class EnrollmentViewSet(BaseModelViewSet):
    """Enrollment view set"""

    resource_name = "enrollments"
    serializer_class = EnrollmentSerializer
    queryset = Enrollment.objects.all()
    permission_classes = [AllowAny]
    http_method_names = ["get"]

    def get_queryset(self, *args, **kwargs):
        return self.queryset.filter()


apps = [EnrollmentViewSet]
