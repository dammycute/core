from django.urls import path
from .views import *
urlpatterns = [
    path('post-property/', CreatePropertyView.as_view()),
    path('post-property/<int:id>/', UpdatePropertyView.as_view()),
    path('property-lists/', PropertyListView.as_view()),
    path('property-lists/<int:pk>/', PropertyDetailView.as_view(), name='property-detail'),
    # path('investments/<int:pk>/sell/', Sell.as_view(), name='investment-sell'),
    path('buy/<int:product_id>/', Buy.as_view(), name='buy'),
    path('investments/', InvestmentListView.as_view(), name='investment-list'),
    path('payment/link/', FlutterwavePaymentLink.as_view(), name='payment_link'),
    path('payment/webhook/', Webhook.as_view(), name='webhook'),
    path('withdraw-to-bank/', WithdrawToBankAPIView.as_view(), name='withdraw-to-bank'),
    # path('property-lists/', PropertyListView.as_view()),
    path('activity/', ActivityEndpoint.as_view(), name='activity')
]