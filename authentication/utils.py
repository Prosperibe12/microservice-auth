from rest_framework.response import Response 
import requests
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_bytes
from django.utils.http import urlsafe_base64_encode
from decouple import config
from django.urls import reverse
from rest_framework.exceptions import NotFound
from rest_framework_simplejwt.tokens import RefreshToken
from authentication import models


class CustomResponse():
    """
    Utility class for creating unified response structure
    """
    
    def Success(data,status=200, headers=None):
        data1 = {
            "data": data,
            "errors": [],
            "message": "Success"       
        }
        return Response(data1, status=status, headers=headers)
    
    def Failure(error, status=400, headers=None):
        data1 = {
            "errors": error,
            "data": [],
            "message": "Failed"
        }
        return Response(data1, status=status, headers=headers)
    
class AuthNotification:
    """ 
    Class for handling registration notfications
    """
    
    @staticmethod
    def _send_email(to_email, subject, message):
        """Utility method to send emails using Mailgun API."""
        try:
            response = requests.post(
                config("MAIL_BASE_URL"),
                auth=("api", config("MAILGUN_SECRET_KEY")),
                data={
                    "from": config("MAIL_SENDER"),
                    "to": [to_email],
                    "subject": subject,
                    "text": message,
                },
            )
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            print(f"Failed to send email to {to_email}: {e}")
            raise

    @staticmethod
    def register_email_notification(payload, domain_name):
        """Send email verification link to the user."""
        try:
            user = models.User.objects.get(id=payload['id'])
        except models.User.DoesNotExist:
            raise NotFound("User does not exist.")

        token = RefreshToken.for_user(user).access_token
        url_path = reverse('verify-email')
        subject = "ACCOUNT VERIFICATION"
        absurl = f'http://{domain_name}{url_path}?token={str(token)}'
        message = f"Hello, \nKindly use the link below to activate your email: \n{absurl}"

        print(f"Sending account verification email \n {message}")
        # return AuthNotification._send_email(user.email, subject, message)
    
    @staticmethod 
    def send_password_reset_email(users, domain_name):
        """Send password reset link to the user."""
        try:
            user = models.User.objects.get(email=users['email'])
        except models.User.DoesNotExist:
            print(f"User with email {users['email']} does not exist.")
            raise NotFound("Inactive User or User Does Not Exist.")

        if not user.is_active:
            print(f"Inactive user {user.email} attempted to reset password.")
            return CustomResponse.Failure("Inactive User")

        uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
        token = PasswordResetTokenGenerator().make_token(user)
        abs_path = reverse('password_reset_confirm', kwargs={'uidb64': uidb64, 'token': token})

        subject = "PASSWORD RESET REQUEST"
        absurl = f'http://{domain_name}{abs_path}'
        message = f"Hello, \nKindly use the link below to reset your password: \n{absurl}"

        print(f"Sending password reset email \n {message}")
        # return AuthNotification._send_email(user.email, subject, message)