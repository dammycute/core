from django.urls import path
from .views import *
urlpatterns = [
    path('post-property/', CreatePropertyView.as_view()),
    path('post-property/<int:id>/', UpdatePropertyView.as_view()),
    path('property-lists/', PropertyListView.as_view()),
    path('property-lists/<int:pk>/', PropertyDetailView.as_view(), name='property-detail'),
    # path('buy/', Buy.as_view()),
    path('buy/<int:product_id>/', Buy.as_view(), name='buy'),
    path('investments/', InvestmentListView.as_view(), name='investment-list'),
    # path('wallet/<int:pk>/', WalletView.as_view(), name='wallet'),
    # path('initiate-payment/', PaystackInitiateView.as_view(), name='initiate-payment'),

]