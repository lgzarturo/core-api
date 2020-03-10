from rest_framework import generics
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings

from .serializers import UserSerializer, AuthTokenSerializer


class CreateUserView(generics.CreateAPIView):
    """Crear un nuevo usuario en el sistema"""
    serializer_class = UserSerializer


class CreateTokenView(ObtainAuthToken):
    """Crear un nuevo token por usuario"""
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES
