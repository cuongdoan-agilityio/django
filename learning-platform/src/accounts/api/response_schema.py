from drf_spectacular.utils import OpenApiResponse, OpenApiExample

from core.serializers import BaseDetailSerializer


user_profile_response_schema = OpenApiResponse(
    response=BaseDetailSerializer,
    description="Returns either instructor, student, or admin profile",
    examples=[
        OpenApiExample(
            "Instructor Profile Example",
            value={
                "data": {
                    "id": "1e80d4c5-f612-4ead-a165-811b1466f03d",
                    "username": "String",
                    "first_name": "String",
                    "last_name": "String",
                    "email": "instructor@example.com",
                    "phone_number": "0652485157",
                    "date_of_birth": "1990-01-01",
                    "gender": "female",
                    "degree": "no",
                    "specializations": [],
                }
            },
            response_only=True,
        ),
        OpenApiExample(
            "Student Profile Example",
            value={
                "data": {
                    "id": "1e80d4c5-f612-4ead-a165-811b1466f03d",
                    "username": "String",
                    "first_name": "String",
                    "last_name": "String",
                    "email": "student@example.com",
                    "phone_number": "0652485157",
                    "date_of_birth": "1990-01-01",
                    "gender": "female",
                    "scholarship": 0,
                }
            },
            response_only=True,
        ),
        OpenApiExample(
            "Admin Profile Example",
            value={
                "data": {
                    "id": "deb00a3f-d4h8-2d74-asvb-bfda19ewf15f",
                    "username": "String",
                    "first_name": "String",
                    "last_name": "String",
                    "email": "admin@example.com",
                    "phone_number": "0652154875",
                    "date_of_birth": "1990-01-01",
                    "gender": "male",
                }
            },
            response_only=True,
        ),
    ],
)

reset_password_response_schema = OpenApiResponse(
    response=BaseDetailSerializer,
    description="Reset password success",
    examples=[
        OpenApiExample(
            "Reset password success",
            value={"data": {"password": "Password"}},
            response_only=True,
        ),
    ],
)
