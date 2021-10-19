from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.signals import user_logged_in
from .models import AerUser

class UserGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = AerUser
        fields = ('id', 'email', 'name',
                  'phone_number', 'image')

class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AerUser
        fields = ('email', 'name',
                  'phone_number', 'image', 'bas64Image', 'imageType', 'address', 'address_latitude', 'address_longitude')

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = AerUser
        fields = ('email', 'password')

    def create(self, validated_data):
        user = AerUser.objects.create_user(
            self.validated_data['email'],
            self.validated_data['password'],
        )
        return user

class LoginSerializer(serializers.Serializer):
    email = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(**data)
        #if user and user.is_subscription paid for store if entering store but, not this:
        if user:
            return user
        raise serializers.ValidationError("Incorrect Credentials")

class ProfileUpdateSrlzr(serializers.ModelSerializer):
    class Meta:
        model = AerUser
        fields = ('name', 'phone_number', 'image', 'base64Image',
                  'imageType', 'address', 'address_latitude', 
                  'address_longitude')

class ProfileGetSrlzr(serializers.ModelSerializer):
    class Meta:
        model = AerUser
        fields = ('id', 'email', 'name', 'phone_number', 'image', 'base64Image',
                  'imageType', 'address', 'address_latitude', 
                  'address_longitude')