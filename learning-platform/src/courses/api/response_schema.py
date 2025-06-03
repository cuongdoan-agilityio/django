from drf_spectacular.utils import OpenApiResponse, OpenApiExample

from core.serializers import BaseDetailSerializer


course_response_schema = OpenApiResponse(
    response=BaseDetailSerializer,
    examples=[
        OpenApiExample(
            "Course Example",
            value={
                "data": {
                    "id": "e77fbdd1-b251-4b0b-8850-79c21ca2aced",
                    "title": "String",
                    "description": "String",
                    "category": {
                        "id": "da544541-1511-4bad-8780-6dcd710a9abb",
                        "name": "string",
                        "description": "string",
                    },
                    "instructor": {
                        "id": "6e3ecf3d-7d0b-46ff-9d69-c081dfc096f8",
                        "username": "string",
                        "first_name": "String",
                        "last_name": "String",
                        "email": "instructor@example.com",
                    },
                    "status": "activate",
                }
            },
            response_only=True,
        )
    ],
)
