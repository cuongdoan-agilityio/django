from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.response import Response
from django.contrib.auth import authenticate, get_user_model
from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
    OpenApiResponse,
    OpenApiExample,
)

from core.api_views import BaseViewSet, BaseModelViewSet
from core.serializers import (
    BaseUnauthorizedResponseSerializer,
    BaseBadRequestResponseSerializer,
    BaseForbiddenResponseSerializer,
)

from students.api.serializers import StudentProfileSerializer
from instructors.api.serializers import InstructorProfileSerializer

from .serializers import (
    LoginRequestSerializer,
    LoginResponseSerializer,
    RegisterSerializer,
    UserProfileUpdateSerializer,
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
            201: StudentProfileSerializer,
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
            return self.ok(response_data)
        else:
            return Response(
                BaseUnauthorizedResponseSerializer(
                    {
                        "errors": [
                            {
                                "field": "email or password",
                                "message": "Invalid credentials.",
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

        if not serializer.is_valid():
            error_details = {}
            for field, errors in serializer.errors.items():
                error_details[field] = errors[0] if isinstance(errors, list) else errors

            return self.bad_request(error_details)

        serializer.is_valid(raise_exception=True)
        user_instance = serializer.save()

        response_serializer = StudentProfileSerializer({"data": user_instance})

        return self.created(response_serializer.data)


class UserViewSet(BaseModelViewSet):
    queryset = User.objects.select_related("student_profile", "instructor_profile")
    permission_classes = [IsAuthenticated]
    serializer_class = InstructorProfileSerializer
    http_method_names = ["get", "patch"]
    resource_name = "users"

    def get_serializer_class(self):
        if self.action in ["retrieve", "partial_update"]:
            user = self.request.user
            if user and hasattr(user, "student_profile"):
                return StudentProfileSerializer
            return InstructorProfileSerializer
        return self.serializer_class

    # TODO: need find another solution to hide the get list method.
    @extend_schema(exclude=True)
    def list(self, request, *args, **kwargs):
        return self.not_allowed()

    @extend_schema(
        description="Retrieve a user profile (Instructor or Student)",
        responses={
            200: OpenApiResponse(
                response=InstructorProfileSerializer,
                description="Returns either Instructor or Student profile",
                examples=[
                    OpenApiExample(
                        "Instructor Profile Example",
                        value={
                            "data": {
                                "uuid": "1e80d4c5-f612-4ead-a165-811b1466f03d",
                                "username": "instructor user name",
                                "first_name": "instructor first name",
                                "last_name": "instructor last name",
                                "email": "instructor@example.com",
                                "phone_number": "0652485157",
                                "date_of_birth": "1990-01-01",
                                "gender": "female",
                                "degree": "no",
                                "subjects": [],
                            }
                        },
                        response_only=True,
                    ),
                    OpenApiExample(
                        "Student Profile Example",
                        value={
                            "data": {
                                "uuid": "1e80d4c5-f612-4ead-a165-811b1466f03d",
                                "username": "instructor user name",
                                "first_name": "instructor first name",
                                "last_name": "instructor last name",
                                "email": "instructor@example.com",
                                "phone_number": "0652485157",
                                "date_of_birth": "1990-01-01",
                                "gender": "female",
                                "scholarship": 0,
                            }
                        },
                        response_only=True,
                    ),
                ],
            )
        },
    )
    def retrieve(self, request, *args, **kwargs):
        serializer = self.get_serializer({"data": request.user})

        return self.ok(serializer.data)

    @extend_schema(
        description="Update the student or instructor profile",
        request=UserProfileUpdateSerializer,
        responses={
            200: OpenApiResponse(
                response=InstructorProfileSerializer,
                description="Returns either Instructor or Student profile",
                examples=[
                    OpenApiExample(
                        "Instructor Profile Example",
                        value={
                            "data": {
                                "first_name": "instructor first name",
                                "last_name": "instructor last name",
                                "phone_number": "0652485157",
                                "date_of_birth": "1990-01-01",
                                "gender": "female",
                                "degree": "no",
                                "subjects": [],
                            }
                        },
                        response_only=True,
                    ),
                    OpenApiExample(
                        "Student Profile Example",
                        value={
                            "data": {
                                "first_name": "instructor first name",
                                "last_name": "instructor last name",
                                "phone_number": "0652485157",
                                "date_of_birth": "1990-01-01",
                                "gender": "female",
                                "scholarship": 0,
                            }
                        },
                        response_only=True,
                    ),
                ],
            ),
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

        pk = kwargs.get("pk")
        if pk != str(user.uuid):
            return self.forbidden()

        serializer = UserProfileUpdateSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        updated_user = User.objects.select_related(
            "student_profile", "instructor_profile"
        ).get(uuid=user.uuid)
        response_serializer = self.get_serializer({"data": updated_user})
        return self.ok(response_serializer.data)


apps = [AuthenticationViewSet, UserViewSet]
