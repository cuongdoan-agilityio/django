from rest_framework.permissions import AllowAny

from core.api_views import BaseModelViewSet
from ..models import Instructor
from .serializers import InstructorSerializer


class InstructorViewSet(BaseModelViewSet):
    """Instructor view set"""

    resource_name = "instructors"
    serializer_class = InstructorSerializer
    queryset = Instructor.objects.all()
    permission_classes = [AllowAny]
    http_method_names = ["get"]

    def get_queryset(self, *args, **kwargs):
        return self.queryset.filter()


apps = [InstructorViewSet]
