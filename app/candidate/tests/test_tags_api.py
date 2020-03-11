from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag
from ..serializers import TagSerializer


TAGS_URL = reverse('candidate:tag-list')


class PublicTagsApiTests(TestCase):
    """Prueba los tags disponibles y publicos"""

    def setUp(self) -> None:
        self.client = APIClient()

    def test_login_required(self):
        """Probar que la autenticacion es requerida para obtener los tags"""
        res = self.client.get(TAGS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsApiTests(TestCase):
    """Prueba la autorizacion para el API de tags"""

    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(
            'test@ghmail.com', 'password123'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retive_tags(self):
        """Obtener los tags"""
        Tag.objects.create(user=self.user, name='Vegan')
        Tag.objects.create(user=self.user, name='Dessert')
        res = self.client.get(TAGS_URL)
        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_to_user(self):
        """Probar que los tags sean del usuario autenticado"""
        other_user = get_user_model().objects.create_user(
            'test2@hotmail.com', 'password1213')
        Tag.objects.create(user=other_user, name='Flurry')
        tag = Tag.objects.create(user=self.user, name='Confort')
        res = self.client.get(TAGS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)