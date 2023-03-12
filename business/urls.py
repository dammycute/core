from django.urls import path
# from .views import UserViewSet
# from rest_framework.routers import DefaultRouter
from .views import *

urlpatterns = [
    path('nin/', NinView.as_view()),
    path('question-detail/', SecurityQuestionView.as_view()),
    path('picture/', PictureView.as_view()),
    path('customer/', CustomerView.as_view(), name='customer'),
    path('profile/', ProfileView.as_view())
]



