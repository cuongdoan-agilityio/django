from drf_spectacular.utils import OpenApiResponse, OpenApiExample

from core.serializers import BaseDetailSerializer


notification_detail_response_schema = OpenApiResponse(
    response=BaseDetailSerializer,
    description="Returns either user notification detail.",
    examples=[
        OpenApiExample(
            "User notification detail",
            value={
                "data": {
                    "id": "1e46d4x5-f643-4gbe-a256-912b5666f93s",
                    "is_read": True,
                    "message": "String",
                }
            },
            response_only=True,
        ),
    ],
)
