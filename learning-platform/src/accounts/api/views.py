from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.response import Response
from rest_framework.mixins import RetrieveModelMixin, UpdateModelMixin
from django.contrib.auth import authenticate, get_user_model
from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
)

from core.api_views import BaseViewSet, BaseGenericViewSet
from core.serializers import (
    BaseUnauthorizedResponseSerializer,
    BaseBadRequestResponseSerializer,
    BaseForbiddenResponseSerializer,
    BaseDetailSerializer,
)
from core.exceptions import ErrorMessage

from instructors.api.serializers import InstructorProfileDataSerializer
from students.api.serializers import StudentProfileDataSerializer

from .response_schema import (
    user_profile_response_schema,
    student_profile_response_schema,
)
from .serializers import (
    LoginRequestSerializer,
    LoginResponseSerializer,
    RegisterSerializer,
    UserProfileUpdateSerializer,
    UserSerializer,
)


User = get_user_model()


@extend_schema_view(
    login=extend_schema(
        description="API to login and get token.",
        request=LoginRequestSerializer,
        responses={
            200: LoginResponseSerializer,
            401: BaseUnauthorizedResponseSerializer,
        },
    ),
    signup=extend_schema(
        description="API to sign up a new user.",
        request=RegisterSerializer,
        responses={
            201: student_profile_response_schema,
            400: BaseBadRequestResponseSerializer,
        },
    ),
)
class AuthenticationViewSet(BaseViewSet):
    """
    A viewset for handling user authentication.

    Provides login and logout actions for users.
    """

    permission_classes = [AllowAny]
    resource_name = "auth"

    @action(detail=False, methods=["post"])
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
            return self.ok(response_data)
        else:
            return Response(
                BaseUnauthorizedResponseSerializer(
                    {
                        "errors": [
                            {
                                "field": "email or password",
                                "message": ErrorMessage.INVALID_CREDENTIALS,
                            }
                        ]
                    }
                ).data,
                status=status.HTTP_401_UNAUTHORIZED,
            )

    @action(detail=False, methods=["post"])
    def signup(self, request):
        """
        Handles sign-up user and returns a success message.

        Args:
            request (HttpRequest): The current request object.

        Returns:
            Response: The response indicating the sign-up status or an error message.
        """

        serializer = RegisterSerializer(data=request.data)

        if not serializer.is_valid():
            error_details = {}
            for field, errors in serializer.errors.items():
                error_details[field] = errors[0] if isinstance(errors, list) else errors

            return self.bad_request(error_details)

        serializer.is_valid(raise_exception=True)
        user_instance = serializer.save()

        response_serializer = BaseDetailSerializer(
            user_instance, context={"serializer_class": StudentProfileDataSerializer}
        )

        return self.created(response_serializer.data)


class UserViewSet(BaseGenericViewSet, RetrieveModelMixin, UpdateModelMixin):
    """
    A viewset for handling user profiles.

    This viewset provides actions to retrieve and update user profiles for both students and instructors.
    It includes custom Swagger documentation for the retrieve and partial_update actions.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = StudentProfileDataSerializer
    http_method_names = ["get", "patch"]
    resource_name = "users"

    def get_serializer_class(self):
        user = self.request.user
        if user and hasattr(user, "student_profile"):
            return StudentProfileDataSerializer
        if user and hasattr(user, "instructor_profile"):
            return InstructorProfileDataSerializer
        return UserSerializer

    def get_queryset(self):
        return User.objects.select_related("student_profile", "instructor_profile")

    @extend_schema(
        description="Retrieve a user profile (Instructor or Student, admin)",
        responses={200: user_profile_response_schema},
    )
    def retrieve(self, request, *args, **kwargs):
        """
        Get the authenticated user's profile.
        """

        user = request.user
        pk = kwargs.get("uuid")

        if pk not in ["me", str(user.uuid)]:
            return self.forbidden()

        serializer = BaseDetailSerializer(
            user, context={"serializer_class": self.get_serializer_class()}
        )
        return self.ok(serializer.data)

    @extend_schema(
        description="Update the student or instructor profile",
        request=UserProfileUpdateSerializer,
        responses={
            200: user_profile_response_schema,
            403: BaseForbiddenResponseSerializer,
        },
    )
    def partial_update(self, request, *args, **kwargs):
        """
        Updates the authenticated user's profile.

        Args:
            request (HttpRequest): The current request object.

        Returns:
            Response: The response indicating the profile update status or an error message.
        """
        user = request.user

        pk = kwargs.get("uuid")
        if pk not in ["me", str(user.uuid)]:
            return self.forbidden()

        serializer = UserProfileUpdateSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        updated_user = self.get_queryset().get(uuid=user.uuid)
        response_serializer = BaseDetailSerializer(
            updated_user, context={"serializer_class": self.get_serializer_class()}
        )
        return self.ok(response_serializer.data)


apps = [AuthenticationViewSet, UserViewSet]
