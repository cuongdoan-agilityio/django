from rest_framework import serializers

from categories.models import Category


class CategorySerializer(serializers.ModelSerializer):
    """
    Serializer for the Category model.
    """

    class Meta:
        model = Category
        fields = ["uuid", "name"]
