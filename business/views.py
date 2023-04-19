from django.shortcuts import render
from rest_framework import generics, permissions, mixins, viewsets, status
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from .serializers import *

from rest_framework.views import APIView


from .models import *
from rest_framework.permissions import IsAuthenticated
# Create your views here.

class IsOwnerOfObject(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj == request.user




# Let's Start Over


from rest_framework.exceptions import ValidationError, PermissionDenied


class CustomerView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CustomerSerializer

    def get_queryset(self):
        user = self.request.user
        return CustomerDetails.objects.filter(user=user)

    def perform_create(self, serializer):
        profile_exists = self.get_queryset().exists()
        if profile_exists:
            raise ValidationError("Profile already exists.")
        serializer.save(user=self.request.user)




class NinView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated,]

    queryset = CustomerDetails.objects.all()
    serializer_class = NinSerializer

    def get_object(self):
        return CustomerDetails.objects.get(user=self.request.user)
#     lookup_field ='id'

class SecurityQuestionView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated,]

    queryset = CustomerDetails.objects.all()
    serializer_class = QuestionSerializer

    def get_object(self):
        return CustomerDetails.objects.get(user=self.request.user)


class PictureView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated,]

    queryset = CustomerDetails.objects.all()
    serializer_class = PictureSerializer

    def get_object(self):
        return CustomerDetails.objects.get(user=self.request.user)


# class ProfileView(generics.RetrieveAPIView):
#     queryset = CustomerDetails.objects.all()
#     serializer_class = CustomerProfileSerializer
#     permission_classes = [IsAuthenticated]

#     def get_object(self):
#         return CustomerDetails.objects.get(user=self.request.user)


# class ProfileViewSet(viewsets.ViewSet):
#     permission_classes = [IsAuthenticated]
#     def list(self, request):
#         user = request.user
#         user
#         bvn = Bvn.objects.get(user=user)
#         nin = Nin.objects.get(user=user)
#         picture = Picture.objects.get(user=user)
#         security = Security.objects.get(user=user)

#         serializer = CustomerProfileSerializer(data={
#             'bvn': bvn,
#             'nin': nin
#         })



# class ProfileView(generics.RetrieveAPIView):
#     permission_classes = [IsAuthenticated,]
#     queryset = CustomerDetails.objects.all()
#     serializer_class = ProfileSerializer

#     def get_object(self):
#         # user_id = self.kwargs['user_id']
#         return self.queryset.filter(user=self.request.user)
    

class ProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated,]
    def get(self, request, format=None):
        user = request.user
        customers = CustomerDetails.objects.filter(user=user)
        serializer = ProfileSerializer(customers, many=True)
        # print(serializer.data)
        return Response(serializer.data)
        
