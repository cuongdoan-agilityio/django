from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.response import Response
from rest_framework.mixins import RetrieveModelMixin, UpdateModelMixin, ListModelMixin
from django.contrib.auth import authenticate, get_user_model
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
)

from accounts.models import Specialization
from core.api_views import BaseViewSet, BaseGenericViewSet
from core.serializers import (
    BaseUnauthorizedResponseSerializer,
    BaseBadRequestResponseSerializer,
    BaseForbiddenResponseSerializer,
    BaseDetailSerializer,
)
from core.error_messages import ErrorMessage

from .response_schema import (
    user_profile_response_schema,
    signup_success_response_schema,
    verify_success_response_schema,
)
from .serializers import (
    LoginRequestSerializer,
    LoginResponseSerializer,
    RegisterSerializer,
    UserProfileUpdateSerializer,
    SpecializationSerializer,
    UserProfileDataSerializer,
    VerifySignupEmailSerializer,
    UserActivateSerializer,
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
            201: signup_success_response_schema,
            400: BaseBadRequestResponseSerializer,
        },
    ),
    verify_email=extend_schema(
        description="API to verify signup email.",
        request=VerifySignupEmailSerializer,
        responses={
            201: verify_success_response_schema,
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
        serializer.save()
        return self.ok()

    @action(detail=False, methods=["post"], url_path="verify-email")
    def verify_email(self, request):
        """
        Verify the email of a user using a token.
        """

        serializer = VerifySignupEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.validated_data["token"]

        if not serializer.is_valid():
            error_details = {}
            for field, errors in serializer.errors.items():
                error_details[field] = errors[0] if isinstance(errors, list) else errors

            return self.bad_request(error_details)

        signer = TimestampSigner()

        try:
            signed_value = force_str(urlsafe_base64_decode(token))
            user_id = signer.unsign(signed_value, max_age=24 * 3600)
            user = User.objects.get(id=user_id)
            serializer = UserActivateSerializer(
                user, data={"is_active": True}, partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return self.ok()

        except (BadSignature, SignatureExpired, User.DoesNotExist):
            return self.bad_request(ErrorMessage.INVALID_TOKEN)


class UserViewSet(BaseGenericViewSet, RetrieveModelMixin, UpdateModelMixin):
    """
    A viewset for handling user profiles.

    This viewset provides actions to retrieve and update user profiles for both students and instructors.
    It includes custom Swagger documentation for the retrieve and partial_update actions.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileDataSerializer
    http_method_names = ["get", "patch"]
    resource_name = "users"

    def get_queryset(self):
        return User.objects.all()

    @extend_schema(
        description="Retrieve a user profile (Instructor or Student, admin) by id. "
        "Call `/api/v1/users/me` to get the authenticated user's profile.",
        responses={
            200: user_profile_response_schema,
            403: BaseForbiddenResponseSerializer,
        },
    )
    def retrieve(self, request, *args, **kwargs):
        """
        Get the authenticated user's profile.
        """

        user = request.user
        pk = kwargs.get("pk")

        if not user.is_superuser and (pk not in ["me", str(user.id)]):
            return self.forbidden()

        user = user if pk == "me" else self.get_queryset().filter(id=pk).first()

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

        pk = kwargs.get("pk")

        if not user.is_superuser and (pk not in ["me", str(user.id)]):
            return self.forbidden()

        try:
            user = user if pk == "me" else User.objects.get(id=pk)
        except User.DoesNotExist:
            return self.bad_request({"student": ErrorMessage.INVALID_USER_ID})

        serializer = UserProfileUpdateSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        updated_user = self.get_queryset().get(id=user.id)
        response_serializer = BaseDetailSerializer(
            updated_user, context={"serializer_class": self.get_serializer_class()}
        )
        return self.ok(response_serializer.data)

    @action(detail=False, methods=["post"], url_path="change-password")
    def change_password(self, request):
        """
        Change the password of a user using a token.
        """
        # Send confirm email to user with token to change password.
        return self.ok()

    @action(detail=False, methods=["post"], url_path="verify-change-password")
    def verify_change_password(self, request):
        """
        Verify change the password of a user using a token.
        """
        # Change the password of the user using the token.
        return self.ok()


class SpecializationViewSet(BaseGenericViewSet, ListModelMixin):
    """
    Specialization view set.
    """

    permission_classes = [AllowAny]
    serializer_class = SpecializationSerializer
    http_method_names = ["get"]
    resource_name = "specializations"

    def get_queryset(self):
        return Specialization.objects.all()


apps = [AuthenticationViewSet, UserViewSet, SpecializationViewSet]
