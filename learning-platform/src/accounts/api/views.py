from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.mixins import RetrieveModelMixin, UpdateModelMixin
from django.contrib.auth import authenticate, get_user_model
from drf_spectacular.utils import extend_schema

from accounts.models import Specialization
from accounts.services import UserServices, AuthenticationServices
from core.api_views import BaseViewSet, BaseGenericViewSet
from core.exceptions import UserException
from core.serializers import (
    BaseUnauthorizedResponseSerializer,
    BaseBadRequestResponseSerializer,
    BaseForbiddenResponseSerializer,
    BaseSuccessResponseSerializer,
    BaseNotFoundResponseSerializer,
)
from core.error_messages import ErrorMessage
from core.permissions import IsOwner
from core.mixins import CustomListModelMixin

from .serializers import (
    LoginRequestSerializer,
    LoginResponseSerializer,
    RegisterSerializer,
    UserProfileUpdateSerializer,
    SpecializationListResponseSerializer,
    UserProfileResponseSerializer,
    ResetUserPasswordSerializer,
    ResetUserPasswordResponseSerializer,
    TokenSerializer,
    ConfirmResetPasswordSerializer,
)

User = get_user_model()


class AuthenticationViewSet(BaseViewSet):
    """
    A viewset for handling user authentication.

    Provides login and logout actions for users.
    """

    permission_classes = [AllowAny]
    resource_name = "auth"

    def get_serializer_class(self):
        if action := self.action:
            if action == "login":
                return TokenSerializer
            if action == "reset_password":
                return ResetUserPasswordResponseSerializer
        return LoginRequestSerializer

    @extend_schema(
        description="API to login and get token.",
        request=LoginRequestSerializer,
        responses={
            200: LoginResponseSerializer,
            400: BaseBadRequestResponseSerializer,
            401: BaseUnauthorizedResponseSerializer,
        },
    )
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
            token, _ = Token.objects.get_or_create(user=user)
            response_data = LoginResponseSerializer({"data": {"token": token.key}})
            return self.ok(response_data.data)

        else:
            inactive_user = User.objects.filter(email=email).first()

            if inactive_user and not inactive_user.is_active:
                return self.bad_request(
                    field="email", message=ErrorMessage.USER_NOT_ACTIVE
                )

            return self.unauthorized_request(
                field="Email or Password",
                message=ErrorMessage.INVALID_CREDENTIALS,
            )

    @extend_schema(
        description="API to sign up a new user.",
        request=RegisterSerializer,
        responses={
            200: BaseSuccessResponseSerializer,
            400: BaseBadRequestResponseSerializer,
        },
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
        serializer.is_valid(raise_exception=True)
        AuthenticationServices().handle_create_user(serializer.validated_data)
        response = BaseSuccessResponseSerializer({"data": {"success": True}})
        return self.ok(response.data)

    @extend_schema(
        description="API to confirm signup email.",
        request=TokenSerializer,
        responses={
            200: BaseSuccessResponseSerializer,
            400: BaseBadRequestResponseSerializer,
        },
    )
    @action(detail=False, methods=["post"], url_path="confirm-signup-email")
    def confirm_signup_email(self, request):
        """
        Confirm the email of a user using a token.
        """

        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        token = serializer.validated_data["token"]
        AuthenticationServices().handle_confirm_signup_email(token)
        response = BaseSuccessResponseSerializer({"data": {"success": True}})
        return self.ok(response.data)

    @extend_schema(
        description="Reset user password using a token.",
        request=ResetUserPasswordSerializer,
        responses={
            200: BaseSuccessResponseSerializer,
            400: BaseBadRequestResponseSerializer,
        },
    )
    @action(detail=False, methods=["post"], url_path="reset-password")
    def reset_password(self, request):
        """
        Confirm reset the password of a user using a token.
        """

        serializer = ResetUserPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        AuthenticationServices().handle_reset_password(
            serializer.validated_data["email"]
        )
        response = BaseSuccessResponseSerializer({"data": {"success": True}})
        return self.ok(response.data)

    @extend_schema(
        description="Confirm reset user password using a token.",
        request=ConfirmResetPasswordSerializer,
        responses={
            200: BaseSuccessResponseSerializer,
            400: BaseBadRequestResponseSerializer,
        },
    )
    @action(detail=False, methods=["POST"], url_path="confirm-reset-password")
    def confirm_reset_password(self, request):
        """
        Reset the password of a user using a token.
        """

        serializer = ConfirmResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        AuthenticationServices().handle_confirm_reset_password(
            token=serializer.validated_data["token"],
            password=serializer.validated_data["password"],
        )
        response = BaseSuccessResponseSerializer({"data": {"success": True}})
        return self.ok(response.data)


class UserViewSet(BaseGenericViewSet, RetrieveModelMixin, UpdateModelMixin):
    """
    A viewset for handling user profiles.

    This viewset provides actions to retrieve and update user profiles for both students and instructors.
    It includes custom Swagger documentation for the retrieve and partial_update actions.
    """

    permission_classes = [IsAuthenticated & IsAdminUser | IsOwner]
    serializer_class = UserProfileResponseSerializer
    http_method_names = ["get", "patch"]
    resource_name = "users"
    queryset = User.objects.all()

    @extend_schema(
        description="Retrieve a user profile (Instructor or Student, admin) by id. "
        "Call `/api/v1/users/me` to get the authenticated user's profile.",
        responses={
            200: UserProfileResponseSerializer,
            401: BaseUnauthorizedResponseSerializer,
            403: BaseForbiddenResponseSerializer,
            404: BaseNotFoundResponseSerializer,
        },
    )
    def retrieve(self, request, *args, **kwargs):
        """
        Get the authenticated user's profile.
        """

        user = request.user
        pk = kwargs.get("pk")

        try:
            user = user if pk == "me" else User.objects.get(id=pk)
        except User.DoesNotExist:
            raise UserException(code="USER_NOT_FOUND")

        self.check_object_permissions(request, user)

        response_data = self.get_serializer({"data": user})
        return self.ok(response_data.data)

    @extend_schema(
        description="Update the student or instructor profile",
        request=UserProfileUpdateSerializer,
        responses={
            200: UserProfileResponseSerializer,
            403: BaseForbiddenResponseSerializer,
            404: BaseNotFoundResponseSerializer,
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

        try:
            user = user if pk == "me" else User.objects.get(id=pk)
        except User.DoesNotExist:
            raise UserException(code="USER_NOT_FOUND")

        self.check_object_permissions(request, user)

        serializer = UserProfileUpdateSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        user = UserServices().update_user_profile(user, serializer.validated_data)
        response_data = self.get_serializer({"data": user})

        return self.ok(response_data.data)


class SpecializationViewSet(BaseGenericViewSet, CustomListModelMixin):
    """
    Specialization view set.
    """

    permission_classes = [AllowAny]
    serializer_class = SpecializationListResponseSerializer
    resource_name = "specializations"
    queryset = Specialization.objects.all().order_by("-modified")


apps = [AuthenticationViewSet, UserViewSet, SpecializationViewSet]
