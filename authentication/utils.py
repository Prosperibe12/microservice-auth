import requests
from rest_framework.response import Response 
from rest_framework.views import exception_handler
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.urls import reverse 
from django.core.mail import send_mail, mail_admins
from django.http import JsonResponse
from rest_framework.exceptions import NotFound, AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken
from decouple import config
from authentication import models

def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    # Update the structure of the response data.
    if response is not None:
        customized_response = {
            "data": [],
            "errors": [],
            "code": response.status_code,
            "message": "Failed"
        }

        # Extract error messages
        if isinstance(response.data, list):
            customized_response['errors'].extend(response.data)
        elif isinstance(response.data, dict):
            if 'detail' in response.data:
                customized_response['errors'].append(response.data.get('detail'))
            else:
                for key, value in response.data.items():
                    if isinstance(value, list):
                        customized_response['errors'].extend(value)
                    else:
                        customized_response['errors'].append(value)

        response.data = customized_response

    return response

# Handle 404 errors
def custom404(request, exception):
    message = 'The resource was not found'
    response =  JsonResponse({
        'errors': message,
        'data': '',
        'status': 'failed',
        'code': 404
    })
    response.status_code = 404 
    # send a notification here
    return response

# custom 500 error
def custom500(request):
    message = 'An error occured, we are working to fix it'
    response =  JsonResponse({
        'errors': message,
        'data': '',
        'status': 'failed',
        'code': 500
    })
    response.status_code = 500
    # send a notification here
    return response

class CustomResponse():
    """
    Utility class for creating unified response structure
    """
    
    def Success(data,status=200, headers=None):
        data1 = {
            "data": data,
            "errors": [],
            "code": status,
            "message": "Success"       
        }
        return Response(data1, status=status, headers=headers)
    
    def Failure(error, status=400, headers=None):
        data1 = {
            "errors": error,
            "data": [],
            "code": status,
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
            send_mail(
                subject, 
                message, 
                config("EMAIL_HOST_USER"), 
                [to_email],
                fail_silently=False
            )
        except Exception as e:
            print(f"Failed to send email to {to_email}: {e}")
            # Notify admins of failure
            mail_admins(
                subject="Cannot Send Registration Mail",
                message="The Send Email functionality is failing, cannot send Auth emails"
            )

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
        return AuthNotification._send_email(user.email, subject, message)
    
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
        return AuthNotification._send_email(user.email, subject, message)
        
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
        return AuthNotification._send_email(user.email, subject, message)