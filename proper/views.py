from django.shortcuts import render
from rest_framework import generics, permissions, viewsets, status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, PermissionDenied
from .serializers import *
import datetime
from dateutil.relativedelta import relativedelta
from rest_framework import exceptions
import requests
from django.urls import reverse
from rest_framework.parsers import MultiPartParser, FormParser

from .models import *
from rest_framework.permissions import IsAuthenticated, IsAdminUser

# Create your views here.

class IsOwnerOfObject(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj == request.user

class CreatePropertyView(generics.ListCreateAPIView):
    permission_classes = [IsAdminUser]
    queryset = Property.objects.all()
    serializer_class = PropertySerializer

    def perform_create(self, serializer):
        serializer.validated_data['user'] = self.request.user
        serializer.save()

class UpdatePropertyView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminUser, IsOwnerOfObject]
    
    queryset = Property.objects.all()
    serializer_class = PropertySerializer
    lookup_field = 'id'

    def perform_update(self, serializer):
        user = self.request.user
        if user.is_staff or serializer.instance.owner == user:
            serializer.save(owner=user)
        else:
            raise PermissionDenied(detail="You do not have permission to update this property.")


class PropertyListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    queryset = Property.objects.all()
    serializer_class = PropertySerializer

    def get_serializer_context(self):
        return {'request': self.request}
    
    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        for property_data in response.data:
            url = reverse('property-detail', args=[property_data['id']])
            full_url = request.build_absolute_uri(url)
            property_data['url'] = full_url
        return response


class PropertyDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Property.objects.all()
    serializer_class = PropertySerializer
    lookup_field = 'pk'

# 

@shared_task
def update_investment_value(investment_id):
    investment = Investment.objects.get(pk=investment_id)
    today = datetime.date.today()
    elapsed_months = (today.year - investment.start_date.year) * 12 + (today.month - investment.start_date.month)
    investment.current_value = investment.total_price * (1 + ((investment.roi / 12) / 100) * elapsed_months)
    investment.save()

class Buy(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Investment.objects.select_related('product').all()
    serializer_class = InvestmentSerializer

    def create(self, request, *args, **kwargs):
        try:
            product_id = kwargs['product_id']  # Get the product ID from the URL
            product = Property.objects.get(pk=product_id)
            # product = Property.objects.get(pk=request.data.get('product'))
            slots = int(request.data.get('slots'))
            if slots <= 0:
                raise ValidationError({'slots': 'Slots must be greater than zero'})
            # if product.is_agreed == False:
            #     raise ValidationError({'Terms': 'Terms and Condition must be accepted'})
            total_price = product.price_per_slot * slots
            roi = product.roi
            
            investment = Investment.objects.create(
                user=self.request.user,
                product=product,
                slots=slots,
                start_date=datetime.date.today(),
                end_date=datetime.date.today() + relativedelta(months=product.duration),
                
            )
            today = datetime.date.today()
            elapsed_months = (today.year - investment.start_date.year) * 12 + (today.month - investment.start_date.month)
            investment.total_price = total_price
            investment.roi = roi
            investment.current_value = total_price * (1 + ((roi / 12) / 100) * elapsed_months)
            investment.save()

            # Trigger Celery task to update current value each month
            update_investment_value.apply_async(args=[investment.id], eta=investment.end_date.replace(day=1))
            return Response({'investment': investment.pk}, status=status.HTTP_201_CREATED)
        except Property.DoesNotExist:
            raise ValidationError({'property': 'Invalid property id'})
        except Exception as e:
            raise ValidationError({'error': str(e)})


class InvestmentListView(generics.ListAPIView):
    queryset = Investment.objects.all()
    serializer_class = InvestmentSerializer

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)




# class PaystackInitiateView(generics.CreateAPIView):
#     serializer_class = TransactionSerializer

#     def perform_create(self, serializer):
#         # get the transaction data from the serializer
#         amount = serializer.validated_data.get('amount')
#         reference = serializer.validated_data.get('reference')

#         #get the secret key
#         api_key = settings.PAYSTACK_SECRET_KEY
        
#         # make a request to Paystack API to initiate the transaction
#         paystack_response = requests.post(
#             "https://api.paystack.co/transaction/initialize",
#             headers={
#                 "Authorization": "Bearer ()".format(api_key),
#                 "Content-Type": "application/json"
#             },
#             json={
#                 "amount": amount,
#                 "reference": reference,
#                 "callback_url": "http://127.0.0.1:8000/proper/investments/",
#             }
#         )

#         # check if the request was successful
#         if paystack_response.status_code == 200:
#             # get the authorization URL from the Paystack response
#             authorization_url = paystack_response.json().get('data').get('authorization_url')

#             # save the transaction to the database
#             serializer.save(status="INITIATED", authorization_url=authorization_url)
#         else:
#             # raise an exception if the request to Paystack API failed
#             raise exceptions.APIException("Failed to initiate the transaction with Paystack")




