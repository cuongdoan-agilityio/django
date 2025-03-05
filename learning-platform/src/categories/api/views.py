from core.api_views import BaseGenericViewSet
from rest_framework.mixins import ListModelMixin
from rest_framework.permissions import AllowAny

from categories.models import Category

from .serializers import CategorySerializer


class CategoryViewSet(BaseGenericViewSet, ListModelMixin):
    """
    Category view set
    """

    permission_classes = [AllowAny]
    serializer_class = CategorySerializer
    http_method_names = ["get"]
    resource_name = "categories"
    lookup_field = "uuid"

    def get_queryset(self):
        return Category.objects.all()


apps = [CategoryViewSet]
