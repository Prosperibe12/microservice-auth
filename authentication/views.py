import json
from rest_framework.views import APIView
from rest_framework import generics 
from rest_framework import status 
from django.db import transaction 
from django.contrib.sites.shortcuts import get_current_site 
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
                return utils.CustomResponse.Success("Registered Sucessfully", status=status.HTTP_201_CREATED)
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