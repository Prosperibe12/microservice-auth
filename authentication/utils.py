import requests
from rest_framework.response import Response 
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.urls import reverse
from rest_framework.exceptions import NotFound, AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken
from decouple import config
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
    def verify_email_notification(payload, domain_name):
        """Send email verification link to the user."""
        try:
            user = models.User.objects.get(id=payload['id'])
        except models.User.DoesNotExist:
            raise NotFound("User does not exist.")

        token = RefreshToken.for_user(user).access_token
        url_path = reverse('verify-email')
        subject = "ACCOUNT VERIFICATION"
        absurl = f'http://{domain_name}{url_path}?token={str(token)}'
        message = f"Hello {user.fullname}, \n Kindly use the link below to activate your email: \n{absurl}"

        print(f"Sending account verification email \n {message}")
        # return AuthNotification._send_email(user.email, subject, message)
    
    @staticmethod 
    def password_reset_notification(users, domain_name):
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
        abs_path = reverse('password-reset-confirm', kwargs={'uidb64': uidb64, 'token': token})

        subject = "PASSWORD RESET REQUEST"
        absurl = f'http://{domain_name}{abs_path}'
        message = f"Hello {user.fullname}, \nKindly use the link below to reset your password: \n{absurl}"

        print(f"Sending password reset email \n {message}")
        # return AuthNotification._send_email(user.email, subject, message)
        
    @staticmethod
    def password_confirm_notification(data):
        # get user from decoded uidb64
        try:
            # decode user
            id = force_str(urlsafe_base64_decode(data['uidb64']))
            user = models.User.objects.get(id=id)
            
            # validate token
            if not PasswordResetTokenGenerator().check_token(user,data['token']):
                raise AuthenticationFailed("Verification Token is invalid or Expired", 401)
        except:
            raise AuthenticationFailed("Cannot Verify the user", 401)
        # prepare email
        subject = "PASSWORD RESET CONFIRMATION"
        message = f"Hello {user.fullname}, \nYour password change request has been successful. If you did not initiate this change, please contact our support team immediately."
        print(message)
        # return AuthNotification._send_email(user.email, subject, message)