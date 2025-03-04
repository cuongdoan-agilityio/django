from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.response import Response
from django.contrib.auth import authenticate, get_user_model
from drf_spectacular.utils import extend_schema, extend_schema_view

from core.api_views import BaseViewSet, BaseModelViewSet
from core.serializers import BaseUnauthorizedResponseSerializer
from core.responses import base_responses

from students.api.serializers import StudentProfileSerializer
from instructors.api.serializers import InstructorProfileSerializer

from .serializers import (
    LoginRequestSerializer,
    LoginResponseSerializer,
    RegisterSerializer,
    DataWrapperSerializer,
    UserProfileUpdateSerializer,
)


User = get_user_model()


@extend_schema_view(
    login=extend_schema(
        description="API to login and get token.",
        request=LoginRequestSerializer,
        responses={
            **base_responses,
            200: LoginResponseSerializer,
        },
    ),
    signup=extend_schema(
        description="API to sign up a new user.",
        request=RegisterSerializer,
        responses={**base_responses, 201: StudentProfileSerializer},
    ),
)
class AuthorViewSet(BaseViewSet):
    """
    A viewset for handling user authentication.

    Provides login and logout actions for users.
    """

    permission_classes = [AllowAny]
    resource_name = "auth"

    @action(detail=False, methods=["post"], permission_classes=[AllowAny])
    def login(self, request):
        """
        Handles user login and returns an authentication token.

        Args:
            request (HttpRequest): The current request object.

        Returns:
            Response: The response containing the authentication token or an error message.
        """

        serializer = LoginRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]
        user = authenticate(request, email=email, password=password)

        if user is not None:
            token, created = Token.objects.get_or_create(user=user)
            response_data = LoginResponseSerializer({"data": {"token": token.key}}).data
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            return Response(
                BaseUnauthorizedResponseSerializer(
                    {
                        "errors": [
                            {
                                "field": "email or password",
                                "message": "Invalid email or password.",
                            }
                        ]
                    }
                ).data,
                status=status.HTTP_401_UNAUTHORIZED,
            )

    @action(detail=False, methods=["post"], permission_classes=[AllowAny])
    def signup(self, request):
        """
        Handles sign-up user and returns a success message.

        Args:
            request (HttpRequest): The current request object.

        Returns:
            Response: The response indicating the sign-up status or an error message.
        """

        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_data = serializer.save()

        response_serializer = StudentProfileSerializer(user_data)

        return self.created(response_serializer.data)


# TODO: need find another solution.
@extend_schema(responses=DataWrapperSerializer)
class UserViewSet(BaseModelViewSet):
    queryset = User.objects.select_related("student_profile", "instructor_profile")
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "patch"]
    resource_name = "users"

    # TODO: need find another solution to hide the get list method.
    @extend_schema(exclude=True)
    def list(self, request, *args, **kwargs):
        return self.not_allowed()

    def retrieve(self, request, *args, **kwargs):
        response_serializer = (
            InstructorProfileSerializer(request.user)
            if request.user.is_instructor
            else StudentProfileSerializer(request.user)
        )

        return self.ok({"data": response_serializer.data})

    def partial_update(self, request, *args, **kwargs):
        """
        Updates the authenticated user's profile.

        Args:
            request (HttpRequest): The current request object.

        Returns:
            Response: The response indicating the profile update status or an error message.
        """
        user = request.user
        serializer = UserProfileUpdateSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        updated_user = User.objects.select_related(
            "student_profile", "instructor_profile"
        ).get(uuid=user.uuid)
        response_serializer = (
            InstructorProfileSerializer(updated_user)
            if updated_user.is_instructor
            else StudentProfileSerializer(updated_user)
        )

        return self.ok({"data": response_serializer.data})


apps = [AuthorViewSet, UserViewSet]
