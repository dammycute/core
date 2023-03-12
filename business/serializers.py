from rest_framework import serializers
from .models import *
# from django.contrib.auth.models import Custom

from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer, UserSerializer as BaseUserSerializer
from django.contrib.auth import get_user_model

User = get_user_model()

class UserCreateSerializer(BaseUserCreateSerializer):
    class Meta(BaseUserCreateSerializer.Meta):
        model = User
        fields = ('id', 'email', 'password')

class UserSerializer(BaseUserSerializer):
    class Meta(BaseUserSerializer.Meta):
        model = User
        fields = ('id', 'email', )
        ref_name = 'business.UserSerializer'

class CustomUserSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        ref_name = 'business.CustomUserSerializer'

class UserDetailSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(many=False, read_only=True)
    # user_id=request.user.id
    class Meta:
        model = CustomerDetails
        fields = ('id', 'user', 'first_name', 'last_name', 'phone_number', 'address', 'city', 'state', 'zipcode', 'birth_date')
        extra_kwargs = {'user': {'unique': True}}



# Let's Start again 


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerDetails
        fields = ('id', 'user', 'first_name', 'last_name', 'phone_number', 'address', 'city', 'state', 'zipcode', 'birth_date')
        read_only_fields = ('id', 'user')



class NinSerializer(serializers.ModelSerializer):
    fpage = serializers.ImageField(max_length=None, allow_empty_file=False, use_url=True)
    bpage = serializers.ImageField(max_length=None, allow_empty_file=False, use_url=True)
    class Meta:
        model = CustomerDetails
        fields = ['nin', 'fpage', 'bpage']
    
class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerDetails
        fields = ['security_question', 'security_answer']


class PictureSerializer(serializers.ModelSerializer):
    picture = serializers.ImageField(max_length=None, allow_empty_file=False, use_url=True)

    class Meta:
        model = CustomerDetails
        fields = ['picture']


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerDetails
        fields = ['id', 'user', 'first_name', 'security_question', 'security_answer', 'last_name', 'phone_number', 'address', 'city', 'state', 'zipcode', 'birth_date', 'nin', 'fpage', 'bpage', 'picture']
    