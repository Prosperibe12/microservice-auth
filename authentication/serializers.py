from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.auth import authenticate 
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from authentication import models 
class RegisterSerializer(serializers.ModelSerializer):
    
    password = serializers.CharField(max_length=128, min_length=6, write_only=True)
    
    class Meta:
        model = models.User 
        fields = ['id','fullname','email','password']
        
    def validate_email(self, value):
        user = models.User.objects.filter(email=value)
        if user.exists():
            raise ValueError(f"User with {value} already exists")
        return value
        
    def create(self, validated_data):
        return models.User.objects.create_user(**validated_data)
    
class EmailVerificationSerializer(serializers.ModelSerializer):
    token = serializers.CharField(max_length=255, required=False)
    
    class Meta:
        model = models.User
        fields = ['token']
        
class LoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255, min_length=3)
    password = serializers.CharField(max_length=128, min_length=6, write_only=True)
    tokens = serializers.DictField(read_only=True)
    
    class Meta:
        model = models.User
        fields = ['email','password','tokens']
        
    def validate(self, attrs):
        email = attrs.get('email', None)
        password = attrs.get('password', None)
        
        # authenticate the user
        user = authenticate(email=email, password=password)
        if user is None:
            raise AuthenticationFailed("Invalid Email or Password")
        if not user.is_verified:
            raise AuthenticationFailed("Email is not verified")
        if not user.is_active:
            raise AuthenticationFailed("Account is not active, Contact Admin")
        return {
            'email': user.email,
            'tokens': user.tokens()
        }

class PasswordResetRequestSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255, min_length=6, required=True)
    
    class Meta:
        model = models.User
        fields = ['email']
        
    def validate(self, value):
        user = models.User.objects.filter(email=value['email'])
        if not user.exists():
            raise serializers.ValidationError("User with this email does not exist")
        return value

class PasswordChangeSerializer(serializers.ModelSerializer):
    password = serializers.CharField(min_length=6, write_only=True)
    token = serializers.CharField(min_length=3, write_only=True)
    uidb64 = serializers.CharField(min_length=3, write_only=True)
    
    class Meta:
        model = models.User 
        fields = ['password','token','uidb64']
        
    def validate(self, attrs):
        # validate password and token
        try:
            password = attrs.get("password")
            token = attrs.get("token")
            uidb64 = attrs.get("uidb64")
            
            # decode user
            id = force_str(urlsafe_base64_decode(uidb64))
            user = models.User.objects.get(id=id)
            
            # validate token
            if not PasswordResetTokenGenerator().check_token(user,token):
                raise AuthenticationFailed("Verification Token is invalid or Expired", 401)
            
            # set new password
            user.set_password(password)
            user.save()
            
            return user
        except Exception as e:
            raise AuthenticationFailed("Invalid or Expired Token")

class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()
    
    default_error_message = {
        'bad_token': ('Token is Expired or Invalid')
    }
    
    def validate(self, attrs):
        self.token = attrs['refresh']
        return attrs
    
    def save(self, **kwargs):
        try:
            RefreshToken(self.token).blacklist() 
        except TokenError:
            self.fail('bad_token')