from django.urls import reverse
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from rest_framework.test import APITestCase
from authentication import models, views

class TestAuthentications(APITestCase):
    """
    Test suite for the authentication service.
    This class uses Django Rest Framework's APIClient to test the authentication views and models.
    """
    def setUp(self):
        # setup urls and data
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.password_reset_request = reverse('password-reset')
        
        self.register_data = {
            "fullname": "Hey There",
            "email": "a@a.com",
            "password": "123456"
        }
        self.bad_register_data = {
            "fullname": "Hey There",
            "email": "a@a.com",
            "password": "12345"
        }
        self.login_data = {
            "email": "a@a.com",
            "password": "123456"
        }
        super().setUp()
    
    def test_create_user_without_email(self):
        with self.assertRaisesMessage(ValueError, 'The Email field must be set'):
            models.User.objects.create_user(password="123456")
            
    def test_create_user(self):
        user = models.User.objects.create_user(fullname="Hey Bob", email="a@a.com", password="123456")
        self.assertIsInstance(user,models.User)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertFalse(user.is_verified)
        self.assertEqual(user.email,"a@a.com")
        
    def test_create_superuser_without_staff_status(self):
        with self.assertRaisesMessage(ValueError, 'Superuser must have is_staff=True'):
            models.User.objects.create_superuser(
                fullname="Hey Admin", 
                email="admin@admin.com", 
                password="123456",
                is_staff=False
            )
    
    def test_create_superuser_without_superuser_status(self):
        with self.assertRaisesMessage(ValueError, 'Superuser must have is_superuser=True'):
            models.User.objects.create_superuser(
                fullname="Hey Admin", 
                email="admin@admin.com", 
                password="123456",
                is_superuser=False
            )
        
    def test_create_superuser(self):
        user = models.User.objects.create_superuser(fullname="Hey Bob", email="admin@admin.com", password="123456")
        self.assertIsInstance(user,models.User)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertEqual(user.email,'admin@admin.com')
        
    def test_user_tokens(self):
        user = models.User.objects.create_user(fullname="Hey Bob", email="a@a.com", password="123456")
        refresh = RefreshToken.for_user(user)
        self.assertIsNotNone(refresh.access_token)
        self.assertIsNotNone(refresh)
        self.assertTrue(isinstance(refresh, RefreshToken))
        self.assertIsNotNone(refresh)
        self.assertIsNotNone(user.tokens())
        
    def test_user_str(self):
        user = models.User.objects.create_user(fullname="Hey Bob", email="a@a.com", password="123456")
        self.assertEqual(str(user), "a@a.com")

    def test_create_user_register(self):
        res = self.client.post(self.register_url, self.register_data, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
    
    def test_create_invalid_user_register(self):
        res = self.client.post(self.register_url, self.bad_register_data, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        
    def test_login_with_unverified_email(self):
        res = self.client.post(self.login_url, self.login_data, format="json")
        self.assertEqual(res.status_code,status.HTTP_403_FORBIDDEN)
        
    def test_login_with_verified_email(self):        
        res = self.client.post(self.register_url, self.register_data, format='json')
        email = self.register_data['email']
        user = models.User.objects.get(email=email)
        user.is_verified = True
        user.save()
        response = self.client.post(self.login_url, self.login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, 'tokens')
        self.assertContains(response, 'email')
    
    def test_password_reset_request(self):
        models.User.objects.create_user(fullname="Hey Bob", email="a@a.com", password="123456")
        res = self.client.post(self.password_reset_request, {"email":"a@a.com"}, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        