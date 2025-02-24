from rest_framework.permissions import AllowAny

from core.api_views import BaseModelViewSet
from ..models import Course
from .serializers import CourseSerializer


class CourseViewSet(BaseModelViewSet):
    """
    Course view set
    """

    resource_name = "courses"
    serializer_class = CourseSerializer
    queryset = Course.objects.all()
    permission_classes = [AllowAny]
    http_method_names = ["get"]

    def get_queryset(self, *args, **kwargs):
        return self.queryset.filter()


apps = [CourseViewSet]
