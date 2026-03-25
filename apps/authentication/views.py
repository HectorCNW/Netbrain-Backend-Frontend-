from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User
from .serializers import RegisterSerializer, LoginSerializer, UserSerializer


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }


@api_view(["POST"])
@permission_classes([AllowAny])
def register(request):
    """Registro de nuevo usuario."""
    serializer = RegisterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    tokens = get_tokens_for_user(user)
    return Response(
        {"user": UserSerializer(user).data, "tokens": tokens},
        status=status.HTTP_201_CREATED,
    )


@api_view(["POST"])
@permission_classes([AllowAny])
def login(request):
    """Login y obtención de tokens JWT."""
    serializer = LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.validated_data["user"]
    tokens = get_tokens_for_user(user)
    return Response({"user": UserSerializer(user).data, "tokens": tokens})


@api_view(["POST"])
@permission_classes([AllowAny])
def refresh_token(request):
    """Refresco del access token."""
    refresh = request.data.get("refresh")
    if not refresh:
        return Response({"error": "Token refresh requerido"}, status=status.HTTP_400_BAD_REQUEST)
    try:
        token = RefreshToken(refresh)
        return Response({"access": str(token.access_token)})
    except Exception:
        return Response({"error": "Token inválido o expirado"}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me(request):
    """Datos del usuario autenticado."""
    return Response(UserSerializer(request.user).data)
