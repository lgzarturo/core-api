from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUserApiTest(TestCase):
    """Prueba de la API publica"""

    def setUp(self) -> None:
        self.client = APIClient()

    def test_create_valid_user_success(self):
        """Probar el envio correcto del usuario"""
        payload = {
            'email': 'test@gmail.com',
            'password': 'test$3616',
            'name': 'Test name'
        }
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_user_exists(self):
        payload = {
            'email': 'test@gmail.com',
            'password': 'test$3616'
        }
        create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """Probando que la contraseña debe ser mayor que 5 caracteres"""
        payload = {
            'email': 'test@gmail.com',
            'password': 'tp',
            'name': 'Test name'
        }
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """Probando que el token se crea para el usuario"""
        payload = {
            'email': 'test@gmail.com',
            'password': 'test$3616',
        }
        create_user(**payload)
        res = self.client.post(TOKEN_URL, payload)
        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_credentials(self):
        """Probando que el token no se cree con credenciales invalidas"""
        create_user(email='test@gmail.com', password='rightPass')
        payload = {
            'email': 'test@gmail.com',
            'password': 'wrongPass',
        }
        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_no_user(self):
        """Probando que no se genere un token con credenciales invalidas"""
        payload = {
            'email': 'test@gmail.com',
            'password': 'wrongPass',
        }
        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_missing_field(self):
        """Probar que el usuario y contraseña son requeridos"""
        payload = {
            'email': 'test',
            'password': '',
        }
        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_unauthorized(self):
        """Probar que se requiere autenticación"""
        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTest(TestCase):
    """Pruebas de la API privada que requiere autenticación"""

    def setUp(self) -> None:
        self.user = create_user(
            email="test@gmail.com", password="test12#12", name="Name")
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrive_profile_success(self):
        """Probar que obtenemos el perfile del usuario autenticado"""
        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'name': self.user.name,
            'email': self.user.email
        })

    def test_post_me_not_allowed(self):
        """Probar que el metodo POST no esta disponible"""
        res = self.client.post(ME_URL, {})
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_profile(self):
        """Probando que el usuario autenticado puede actualizar su info"""
        payload = {
            'email': 'test@gmail.com',
            'password': 'newPass',
            'name': 'testApp'
        }
        res = self.client.patch(ME_URL, payload)
        self.user.refresh_from_db()
        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
