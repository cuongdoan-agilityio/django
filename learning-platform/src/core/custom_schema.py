from drf_spectacular.extensions import OpenApiSerializerExtension


class CustomDataWrapper(OpenApiSerializerExtension):
    target_class = "./core/serializers.BaseDetailSerializer"

    def get_name(self):
        return "DataWrapper"

    def get_schema(self, direction):
        schema = super().get_schema(direction)
        return {"type": "object", "properties": {"data": schema}}
