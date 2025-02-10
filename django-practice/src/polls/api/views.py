from rest_framework.permissions import AllowAny

from core.api_views import BaseModelViewSet
from ..models import Poll
from .serializers import PollSerializer


class PollViewSet(BaseModelViewSet):
    """Poll view set"""

    resource_name = "polls"
    serializer_class = PollSerializer
    queryset = Poll.objects.all()
    permission_classes = [AllowAny]
    http_method_names = ["get"]

    def get_queryset(self, *args, **kwargs):
        return self.queryset.filter()


apps = [PollViewSet]
