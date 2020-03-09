from django.test import TestCase
from django.contrib.auth import get_user_model


class ModelTests(TestCase):

    def test_create_user_with_email_successful(self):
        """Probar la creación de un usuario, con un correo valido"""
        email = "lgzarturo@gmail.com"
        password = "TestPass#12345"
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalize(self):
        """Prueba para normalizar direcciones de correos"""
        email = "test@GmaiL.COM"
        user = get_user_model().objects.create_user(email, 'test#17126')
        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        """Prueba creando un usuario con un correo invalido"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, 'test#17126')

    def test_create_new_superuser(self):
        """Para crear un super usuario"""
        user = get_user_model().objects.create_superuser('test@gmail.com',
                                                         'test#17126')
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
