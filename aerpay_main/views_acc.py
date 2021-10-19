from rest_framework import generics, permissions, status
from aerpay_main.acc_serializers import LoginSerializer, ProfileGetSrlzr, ProfileUpdateSrlzr, RegisterSerializer, UserGetSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
from knox.models import AuthToken
from knox.auth import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.signals import user_logged_out

from view_functions import putWithImage

class RegisterAPI(generics.GenericAPIView):
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        myResponse = Response({
            "message": "success",
            'data': {"user": UserGetSerializer(
                user,
                context=self.get_serializer_context()
            ).data,
                "token": AuthToken.objects.create(user)[1]}
        })
        if myResponse.status_code == 200:
            return myResponse
        else:
            return Response({'message': 'Failed'})

class LoginAPI(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data

        myResponse = Response({
            "message": "success",
            'data': {"user": UserGetSerializer(
                user,
                context=self.get_serializer_context()
            ).data,
                "token": AuthToken.objects.create(user)[1]}
        })
        if myResponse.status_code == 200:
            return myResponse
        else:
            return Response({'message': 'Failed'})

class Logout(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):
        myUser = request.user
        request._auth.delete()
        user_logged_out.send(sender=myUser.__class__,
                             request=request, user=myUser)
        myResponse = Response({
            "message": "success",
            'data': 'logged out'
        })
        if myResponse.status_code == 200:
            return myResponse
        else:
            return Response({'message': 'Failed'})

class ProfileUpdateView(APIView):
    permission_classes = [
        permissions.IsAuthenticated,
    ]

    serializer_class = ProfileUpdateSrlzr

    def post(self, request, *args, **kwargs):
        myUser = request.user
        mySerialized = ProfileUpdateSrlzr(myUser, data=request.data)
        mySerialized.is_valid(raise_exception=True)
        putData = putWithImage(mySerialized, myUser, 'profile') 
        return Response({'message': 'success', 'data': putData})

class ProfileGetView(APIView):
    permission_classes = [
        permissions.IsAuthenticated,
    ]

    def get(self, request, *args, **kwargs):
        myUser = request.user
        mySerialized = ProfileGetSrlzr(
            myUser)
        myResponse = Response(
            {'message': 'success', 'data': mySerialized.data})
        return myResponse