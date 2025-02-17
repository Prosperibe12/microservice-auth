from rest_framework import serializers
from authentication import models

class RegisterSerializer(serializers.ModelSerializer):
    
    password = serializers.CharField(max_length=128, min_length=6, write_only=True)
    
    class Meta:
        model = models.User 
        fields = ['id','fullname','email','password']
        
    def validate_email(self, value):
        user = models.User.objects.filter(email=value)
        if user.exists():
            raise serializers.ValidationError(f"User with {value} already exists")
        return value
        
    def create(self, validated_data):
        return models.User.objects.create_user(**validated_data)
    
class EmailVerificationSerializer(serializers.ModelSerializer):
    token = serializers.CharField(max_length=255)
    
    class Meta:
        model = models.User
        fields = ['token']