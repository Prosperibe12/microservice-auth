from rest_framework import generics, status, permissions
from django.db import transaction 
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode
import jwt

from authentication import serializers, utils, tasks, models
from django.conf import settings

class RegisterView(generics.GenericAPIView):
    """
    View that handles new user Registration
    """
    authentication_classes = ()
    permission_classes = ()
    serializer_class = serializers.RegisterSerializer
    
    def post(self, request):
        data = request.data 
        serializers = self.serializer_class(data=data)
        # use atomicity to rollback the transaction if an error occurs
        with transaction.atomic():
            if serializers.is_valid(raise_exception=True):
                serializers.save()
                # get site domain name
                domain_name = get_current_site(request).domain 
                # queue the task to send the email
                tasks.send_email_verification_link.delay_on_commit(serializers.data, domain_name)
                return utils.CustomResponse.Success("Registration Sucessful, Please Verify your Email.", status=status.HTTP_201_CREATED)
            return utils.CustomResponse.Failure(serializers.errors, status=status.HTTP_400_BAD_REQUEST)

class VerifyEmailView(generics.GenericAPIView):
    """
    This view handles email verification logic and set the user account to is_active=True
    """
    authentication_classes = ()
    permission_classes = ()
    serializer_class = serializers.EmailVerificationSerializer
    
    def get(self, request):
        # get the token from the query params
        token = request.query_params.get('token')
        # decode the token
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            # get the user id from the payload
            user = models.User.objects.get(id=payload['user_id'])
            # set the user is_verified to True
            if not user.is_verified:
                user.is_verified = True
                user.save()
            return utils.CustomResponse.Success("Email Verified Successfully", status=status.HTTP_200_OK)
        except jwt.ExpiredSignatureError as e:
            return utils.CustomResponse.Failure("Token Expired", status=status.HTTP_400_BAD_REQUEST)
        except jwt.DecodeError as e:
            return utils.CustomResponse.Failure("Invalid Token", status=status.HTTP_400_BAD_REQUEST)

class LoginView(generics.GenericAPIView):
    """
    The Login view accepts a user email and password,
    validates the user credentials and returns an access token
    """
    authentication_classes = ()
    permission_classes = ()
    serializer_class = serializers.LoginSerializer
    
    def post(self, request):
        serializers = self.serializer_class(data=request.data)
        if serializers.is_valid(raise_exception=True):
            return utils.CustomResponse.Success(serializers.data, status=status.HTTP_200_OK)
        return utils.CustomResponse.Failure(serializers.errors, status=status.HTTP_400_BAD_REQUEST)

class PasswordResetRequest(generics.GenericAPIView):
    """
    This view handles the logic for sending a password reset link to the user email
    """
    authentication_classes = ()
    permission_classes = ()
    serializer_class = serializers.PasswordResetRequestSerializer
    
    def post(self, request):
        serializers = self.serializer_class(data=request.data)
        if serializers.is_valid(raise_exception=True):
            # get the site domain name
            domain_name = get_current_site(request).domain
            # queue the task to send the password reset link
            tasks.send_password_reset_link.delay(serializers.validated_data, domain_name)
            return utils.CustomResponse.Success("Password Reset Link Sent Successfully", status=status.HTTP_200_OK)
        return utils.CustomResponse.Failure(serializers.errors, status=status.HTTP_400_BAD_REQUEST)

class PasswordResetConfirm(generics.GenericAPIView):
    """ 
    Password reset view, takes the uidb64 and user enconded token, decodes
    them and validate user details.
    """
    authentication_classes = ()
    permission_classes = ()
    serializer_class = serializers.PasswordResetRequestSerializer
    
    def get(self, request, uidb64, token):
        # decode tokens
        try:
            id = smart_str(urlsafe_base64_decode(uidb64))
            user = models.User.objects.get(id=id)
            # validate that user token has not been used
            if not PasswordResetTokenGenerator().check_token(user,token):
                return utils.CustomResponse.Failure("Verification Token is invalid or Expired", status=status.HTTP_400_BAD_REQUEST)
            
            payload = {
                "uidb64": uidb64,
                "token": token
            }
            return utils.CustomResponse.Success(payload, status=status.HTTP_200_OK)
        except DjangoUnicodeDecodeError as e:
            return utils.CustomResponse.Failure("Token not Valid", status=status.HTTP_400_BAD_REQUEST)
        
class PasswordChangeView(generics.GenericAPIView):
    """ 
    This view perform password change and sets user new password.
    """
    authentication_classes = ()
    permission_classes = ()
    serializer_class = serializers.PasswordChangeSerializer

    def patch(self, request):
        serializers = self.serializer_class(data=request.data)
        if serializers.is_valid(raise_exception=True):
            return utils.CustomResponse.Success("Password Changed Successfully", status=status.HTTP_200_OK)
        return utils.CustomResponse.Failure(serializers.errors, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(generics.GenericAPIView):
    """
    This view handles user logout by blacklisting the refresh token
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.LogoutSerializer

    def post(self, request):
        serializers = self.serializer_class(data=request.data)
        if serializers.is_valid(raise_exception=True):
            serializers.save()
            return utils.CustomResponse.Success("Logout Successful", status=status.HTTP_204_NO_CONTENT)
        return utils.CustomResponse.Failure(serializers.errors, status=status.HTTP_400_BAD_REQUEST)
    