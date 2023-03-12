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

class UserDetailView(CreateModelMixin, RetrieveModelMixin, UpdateModelMixin, viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated, IsOwnerOfObject]

    queryset = CustomerDetails.objects.all()
    serializer_class = UserDetailSerializer
    

    
    @action(detail=False, methods=['POST'])
    def perform_create(self, request, ):
        # (customer) = CustomerDetails.objects.create(user=request.user, **request.data) 
        if request.method == 'POST':
            serializer = UserDetailSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(user= self.request.user)
            return Response(serializer.data)
    #     try:
    #         with transaction.atomic():
    #             customers = CustomerDetails.objects.get(user=self.request.user)
    #             return Response({"details": "Customer Details already exist."})
    #     except CustomerDetails.DoesNotExist:

    #         serializer.save(user=self.request.user)

    @action(detail=False, methods=['GET', 'PUT'])
    def me(self, request):
        (customer, created) = CustomerDetails.objects.get_or_create(user_id=request.user.id) 
        if request.method == 'GET':
            serializer = UserDetailSerializer(customer)
            return Response(serializer.data)
        elif request.method == 'PUT':
            serializer = UserDetailSerializer(customer, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)


# Let's Start Over

class CustomerView(APIView):
    permission_classes = [IsAuthenticated,]

    def post(self, request):
        try:
            profile = CustomerDetails.objects.get(user=self.request.user)
            return Response({"detail": "Profile already exists."}, status=status.HTTP_409_CONFLICT)
        except CustomerDetails.DoesNotExist:
            serializer = CustomerSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(user=self.request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




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
        
