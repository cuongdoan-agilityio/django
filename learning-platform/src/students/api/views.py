from rest_framework.permissions import AllowAny

from core.api_views import BaseModelViewSet
from ..models import Student
from .serializers import StudentSerializer


class StudentViewSet(BaseModelViewSet):
    """Poll view set"""

    resource_name = "students"
    serializer_class = StudentSerializer
    queryset = Student.objects.all()
    permission_classes = [AllowAny]
    http_method_names = ["get"]

    def get_queryset(self, *args, **kwargs):
        return self.queryset.filter()


apps = [StudentViewSet]
