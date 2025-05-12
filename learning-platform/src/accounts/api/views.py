from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.mixins import RetrieveModelMixin, UpdateModelMixin, ListModelMixin
from django.contrib.auth import authenticate, get_user_model
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.forms.models import model_to_dict
from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
)

from accounts.tasks import send_welcome_email, send_password_reset_email
from accounts.models import Specialization
from core.api_views import BaseViewSet, BaseGenericViewSet
from core.mixins import FormatDataMixin
from core.serializers import (
    BaseUnauthorizedResponseSerializer,
    BaseBadRequestResponseSerializer,
    BaseForbiddenResponseSerializer,
    BaseSuccessResponseSerializer,
    BaseNotFoundResponseSerializer,
    BaseDetailSerializer,
)
from core.error_messages import ErrorMessage
from core.helpers import create_token

from .response_schema import (
    user_profile_response_schema,
    signup_success_response_schema,
    verify_success_response_schema,
    reset_password_response_schema,
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
    ResetUserPasswordSerializer,
    VerifyResetUserPasswordSerializer,
    ResetUserPasswordResponseSerializer,
    LoginResponseDataSerializer,
)

User = get_user_model()


@extend_schema_view(
    login=extend_schema(
        description="API to login and get token.",
        request=LoginRequestSerializer,
        responses={
            200: LoginResponseSerializer,
            400: BaseBadRequestResponseSerializer,
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
    verify_signup_email=extend_schema(
        description="API to verify signup email.",
        request=VerifySignupEmailSerializer,
        responses={
            201: verify_success_response_schema,
            400: BaseBadRequestResponseSerializer,
        },
    ),
    verify_reset_password=extend_schema(
        description="Verify reset password of a user using a token.",
        request=VerifyResetUserPasswordSerializer,
        responses={
            200: BaseSuccessResponseSerializer,
            400: BaseBadRequestResponseSerializer,
        },
    ),
    reset_password=extend_schema(
        description="Reset the password of a user using a token.",
        request=ResetUserPasswordSerializer,
        responses={
            200: reset_password_response_schema,
            400: BaseBadRequestResponseSerializer,
        },
    ),
)
class AuthenticationViewSet(BaseViewSet, FormatDataMixin):
    """
    A viewset for handling user authentication.

    Provides login and logout actions for users.
    """

    permission_classes = [AllowAny]
    resource_name = "auth"

    def get_serializer_class(self):
        if action := self.action:
            if action == "login":
                return LoginResponseDataSerializer
            if action == "reset_password":
                return ResetUserPasswordResponseSerializer
        return LoginRequestSerializer

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
            response_data = self.format_data({"token": token.key})

            return self.ok(response_data)
        else:
            inactive_user = User.objects.filter(email=email).first()

            if not inactive_user.is_active:
                return self.bad_request(
                    field="Email", message=ErrorMessage.USER_NOT_ACTIVE
                )

            return self.unauthorized_request(
                field="Email or Password",
                message=ErrorMessage.INVALID_CREDENTIALS,
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
        serializer.save()
        return self.ok()

    @action(detail=False, methods=["post"], url_path="verify-signup-email")
    def verify_signup_email(self, request):
        """
        Verify the email of a user using a token.
        """

        serializer = VerifySignupEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        token = serializer.validated_data["token"]
        signer = TimestampSigner()

        try:
            signed_value = force_str(urlsafe_base64_decode(token))
            user_id = signer.unsign(signed_value, max_age=24 * 3600)
            user = User.objects.get(id=user_id)
            if not user.is_active:
                serializer = UserActivateSerializer(
                    user, data={"is_active": True}, partial=True
                )
                serializer.is_valid(raise_exception=True)
                serializer.save()
                user_data = model_to_dict(user, fields=["username", "email"])
                send_welcome_email.delay(user_data)
            return self.ok()

        except (BadSignature, SignatureExpired, User.DoesNotExist, ValueError):
            return self.bad_request(field="token", message=ErrorMessage.TOKEN_INVALID)

    @action(detail=False, methods=["post"], url_path="verify-reset-password")
    def verify_reset_password(self, request):
        """
        Verify reset the password of a user using a token.
        """

        serializer = VerifyResetUserPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]

        user = User.objects.filter(email=email).first()

        if not user:
            return self.bad_request(field="email", message=ErrorMessage.USER_NOT_FOUND)

        token = create_token(user.email)

        try:
            send_password_reset_email.delay(
                {"username": user.username, "email": user.email},
                token,
            )
            return self.ok()
        except Exception as e:
            return self.bad_request(message=str(e))

    @action(detail=False, methods=["post"], url_path="reset-password")
    def reset_password(self, request):
        """
        Reset the password of a user using a token.
        """

        serializer = ResetUserPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        token = serializer.validated_data["token"]

        signer = TimestampSigner()

        try:
            signed_value = force_str(urlsafe_base64_decode(token))
            email = signer.unsign(signed_value, max_age=24 * 3600)
            user = User.objects.filter(email=email).first()
            # TODO: need replace with other password
            new_password = "Password@123"
            user.password = new_password
            user.save()
            response_data = self.format_data({"password": new_password})
            return self.ok(response_data)

        except (BadSignature, SignatureExpired, User.DoesNotExist, ValueError):
            return self.bad_request(field="token", message=ErrorMessage.TOKEN_INVALID)


class UserViewSet(
    BaseGenericViewSet, FormatDataMixin, RetrieveModelMixin, UpdateModelMixin
):
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

        if not user.is_superuser and (pk not in ["me", str(user.id)]):
            return self.forbidden()

        user = user if pk == "me" else self.get_queryset().filter(id=pk).first()
        if not user:
            return self.not_found(message=ErrorMessage.USER_NOT_FOUND)

        response_data = self.format_data(user)
        return self.ok(response_data)

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
