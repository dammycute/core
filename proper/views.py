from django.shortcuts import render
from rest_framework import generics, permissions, viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError, PermissionDenied
from .serializers import *
import uuid
from django.contrib.auth.mixins import LoginRequiredMixin
# from django.views.generic.edit import CreateAPIView
import datetime
from dateutil.relativedelta import relativedelta
from rest_framework import exceptions
import requests
from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework.generics import get_object_or_404
from rest_framework import status
from django.urls import reverse
from rest_framework.parsers import MultiPartParser, FormParser
from celery import shared_task
from django.http import JsonResponse
from .models import *
from rest_framework.permissions import IsAuthenticated, IsAdminUser

# Create your views here.

class IsOwnerOfObject(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj == request.user


from django.db.models import Sum

class DashboardView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, format=None):
        wallet = Wallet.objects.filter(user=request.user).first()
        investments = Investment.objects.filter(user=request.user).aggregate(total_amount=Sum('current_value'))['total_amount']

        data = {
            'wallet_balance': wallet.balance if wallet else None,
            'investment': investments,
        }

        return Response(data)

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


# ======= Buy View ==========eqqqweeqqq

from django.db import transaction

class Buy(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Investment.objects.select_related('product').all()
    serializer_class = InvestmentSerializer

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        try:
            product_id = kwargs['product_id']  # Get the product ID from the URL
            product = Property.objects.get(pk=product_id)
            slots = int(request.data.get('slots'))
            if slots <= 0:
                raise ValidationError({'slots': 'Slots must be greater than zero'})
            total_price = product.price_per_slot * slots
            roi = product.roi
            
            wallet = Wallet.objects.select_for_update().get(user=self.request.user)
            if wallet.balance < total_price:
                raise ValidationError({'wallet': 'Insufficient funds'})
            wallet.balance -= total_price
            wallet.save()

            investment = Investment.objects.create(
                user=self.request.user,
                product=product,
                slots=slots,
                start_date=datetime.date.today(),
                end_date=datetime.date.today() + relativedelta(months=product.duration),
            )
            today = datetime.date.today()
            investment.total_price = total_price
            investment.roi = roi
            elapsed_months = (today.year - investment.start_date.year) * 12 + (today.month - investment.start_date.month)
            investment.current_value = total_price * (1 + ((roi / 12) / 100) * elapsed_months)
            investment.save()

            # Trigger Celery task to update current value each month
            update_investment_value.apply_async(args=[investment.id], eta=investment.end_date.replace(day=1))
            return Response({'investment': investment.pk}, status=status.HTTP_201_CREATED)
        except Property.DoesNotExist:
            raise ValidationError({'property': 'Invalid property id'})
        # except Wallet.DoesNotExist:
        #     raise ValidationError({'wallet': 'Wallet not found for the user'})
        except Exception as e:
            raise ValidationError({'error': str(e)})
        

# ======== Sell Endpoint=========

class Sell(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, investment_id):
        try:
            investment = Investment.objects.select_related('product').get(pk=investment_id)
            seller = investment.user
            buyer_id = request.data.get('buyer')
            buyer = CustomUser.objects.get(pk=buyer_id)
            if seller == buyer:
                raise ValidationError({'buyer': 'You cannot sell to yourself'})

            price = investment.total_price

            # check if buyer has enough funds in their wallet
            buyer_wallet = Wallet.objects.filter(user=buyer).first()
            if not buyer_wallet or buyer_wallet.balance < price:
                raise ValidationError({'buyer': 'Insufficient funds to buy investment'})

            with transaction.atomic():
                # deduct amount from buyer's wallet
                buyer_wallet.balance -= price
                buyer_wallet.save()

                # credit amount to seller's wallet
                seller_wallet = Wallet.objects.filter(user=seller).first()
                if not seller_wallet:
                    seller_wallet = Wallet.objects.create(user=seller, balance=0)
                seller_wallet.balance += price
                seller_wallet.save()

                # create a new Investment object for the buyer
                new_investment = Investment.objects.create(
                    user=buyer,
                    product=investment.product,
                    slots=investment.slots,
                    start_date=investment.start_date,
                    end_date=investment.end_date,
                    total_price=investment.total_price,
                    roi=investment.roi
                )

                # Trigger Celery task to update current value each month for new investment
                update_investment_value.apply_async(args=[new_investment.id], eta=new_investment.end_date.replace(day=1))

                # delete the original investment
                investment.delete()

            return Response({'message': 'Investment sold successfully'}, status=status.HTTP_200_OK)
        except Investment.DoesNotExist:
            raise ValidationError({'investment': 'Invalid investment id'})
        # except CustomUser.DoesNotExist:
        #     raise ValidationError({'buyer': 'Invalid buyer id'})
        except Exception as e:
            raise ValidationError({'error': str(e)})




# ==================== This is the Endpoint that list out the investment of the user===========

class InvestmentListView(generics.ListAPIView):
    queryset = Investment.objects.all()
    serializer_class = InvestmentSerializer

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

# ==========================Flutterwave Payment Endpoint====================

# from django.shortcuts import redirect

# class FlutterwavePaymentLink(APIView):
#     serializer_class = TransactionSerializer
#     queryset = Transaction.objects.all()
    
#     def post(self, request, *args, **kwargs):
#         serializer = self.serializer_class(data=request.data)
#         serializer.is_valid(raise_exception=True)

#         # Save the Transaction object to the database
#         transaction = serializer.save()
        
#         # Generate the tx_ref and payment URL
#         tx_ref = uuid.uuid4().hex
#         amount = request.data.get('amount')
#         if not amount:
#             return Response({"error": "Amount not provided"}, status=400)
        
#         url = "https://api.flutterwave.com/v3/payments"
#         headers = {
#             "Authorization": f'Bearer {settings.FLUTTERWAVE_SECRET_KEY}',
#             "Content-Type": "application/json"
#         }

#         payload = {
#             "tx_ref": tx_ref,
#             "amount": str(amount),
#             "currency": "NGN",
#             "redirect_url": "https://www.realowndigital.com/",
#             "payment_options": "card",
#             "meta": {
#                 "consumer_id": request.user.id,
#                 "consumer_mac": "92a3-912ba-1192a"
#             },
#             "customer": {
#                 "email": request.user.email,
#             },
#             "customizations": {
#                 "title": "RealOwn",
#                 "description": "Payment for RealOwn",
#                 "logo": "https://drive.google.com/file/d/1dIWGQYH3ayKiG_xUw-JQuXSt2cfuu4HF/view?usp=drivesdk"
#             }
#         }

#         # Make a request to Flutterwave's API to create the payment link
#         response = requests.post(url, headers=headers, json=payload)

#         try:
#             payment_url = response.json()["data"]["link"]
#         except (ValueError, KeyError):
#             return Response({"error": "An error occurred while processing your request. Please try again later."}, status=500)
        
#         # Redirect the user to the payment URL
#         return redirect(payment_url)


# from django.shortcuts import redirect
# import uuid
# import requests
# from django.conf import settings

# class FlutterwavePaymentLink(generics.CreateAPIView):
#     serializer_class = TransactionSerializer

#     def create(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)

#         # Save the Transaction object to the database
#         transaction = serializer.save()

#         # Generate the tx_ref and payment URL
#         tx_ref = uuid.uuid4().hex
#         amount = serializer.validated_data['amount']
#         if not amount:
#             return Response({"error": "Amount not provided"}, status=400)

#         url = "https://api.flutterwave.com/v3/payments"
#         headers = {
#             "Authorization": f'Bearer {settings.FLUTTERWAVE_SECRET_KEY}',
#             "Content-Type": "application/json"
#         }

#         payload = {
#             "tx_ref": tx_ref,
#             "amount": str(amount),
#             "currency": "NGN",
#             "redirect_url": "https://www.realowndigital.com/",
#             "payment_options": "card",
#             "meta": {
#                 "consumer_id": request.user.id,
#                 "consumer_mac": "92a3-912ba-1192a"
#             },
#             "customer": {
#                 "email": request.user.email,
#             },
#             "customizations": {
#                 "title": "RealOwn",
#                 "description": "Payment for RealOwn",
#                 "logo": "https://drive.google.com/file/d/1dIWGQYH3ayKiG_xUw-JQuXSt2cfuu4HF/view?usp=drivesdk"
#             }
#         }

#         # Make a request to Flutterwave's API to create the payment link
#         response = requests.post(url, headers=headers, json=payload)

#         try:
#             payment_url = response.json()["data"]["link"]
#         except (ValueError, KeyError):
#             return Response({"error": "An error occurred while processing your request. Please try again later."}, status=500)

#         # Redirect the user to the payment URL
#         return redirect(payment_url + f"?amount={amount}")


from django.shortcuts import redirect
from django.db import transaction
import uuid
import requests
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response

from .serializers import TransactionSerializer
from .models import *
from django.contrib.auth import get_user_model

class FlutterwavePaymentLink(CreateAPIView):
    serializer_class = TransactionSerializer

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Save the Transaction object to the database with a 
        User = request.user
        customer = CustomerDetails.objects.get(user=request.user)
        wallet = Wallet.objects.get(user=request.user)
        transaction = Transaction.objects.create(
            user=User,
            customer=customer,
            amount=serializer.validated_data['amount'],
            status=Transaction.PENDING,
            tx_ref=uuid.uuid4().hex,
            wallet=wallet
        )
        tx_ref = transaction.tx_ref

        amount = serializer.validated_data['amount']
        if not amount:
            return Response({"error": "Amount not provided"}, status=400)

        url = "https://api.flutterwave.com/v3/payments"
        headers = {
            "Authorization": f'Bearer {settings.FLUTTERWAVE_SECRET_KEY}',
            "Content-Type": "application/json"
        }

        payload = {
            "tx_ref": tx_ref,
            "amount": str(amount),
            "currency": "NGN",
            "redirect_url": "http://htcode12.pythonanywhere.com/",
            "payment_options": "card",
            "meta": {
                "consumer_id": request.user.id,
                "consumer_mac": "92a3-912ba-1192a"
            },
            "customer": {
                "email": request.user.email,
                "customer_name": customer.first_name + customer.last_name
            },
            "customizations": {
                "title": "RealOwn",
                "description": "Payment for RealOwn",
                "logo": "https://drive.google.com/file/d/1dIWGQYH3ayKiG_xUw-JQuXSt2cfuu4HF/view?usp=drivesdk"
            },
            "callback_url": request.build_absolute_uri(reverse('webhook'))
        }

        # Make a request to Flutterwave's API to create the payment link
        response = requests.post(url, headers=headers, json=payload)

        try:
            payment_url = response.json()["data"]["link"]
        except (ValueError, KeyError):
            # Update the transaction status to failed if the payment link cannot be generated
            transaction.status = Transaction.FAILED
            transaction.save()
            return Response({"error": "An error occurred while processing your request. Please try again later."}, status=500)

        # Redirect the user to the payment URL
        return redirect (payment_url + f"?amount={amount}")



# Webhook View

# from django.views.decorators.csrf import csrf_exempt
# from django.http import HttpResponseBadRequest, HttpResponse
# from rest_framework.views import APIView
# from rest_framework.permissions import AllowAny
# from .models import Transaction

# class FlutterwaveWebhook(APIView):
#     permission_classes = [AllowAny,]
#     @csrf_exempt
#     def post(self, request):
#         # Retrieve the transaction reference and status from the webhook payload
#         tx_ref = request.data.get('tx_ref')
#         status = request.data.get('status')

#         # Retrieve the corresponding transaction from the database
#         transaction = Transaction.objects.filter(tx_ref=tx_ref).first()
#         if not transaction:
#             return HttpResponseBadRequest('Transaction not found')

#         # Update the transaction status based on the webhook payload
#         if status == 'successful':
#             transaction.status = Transaction.COMPLETED
#             # Add the transaction amount to the user's wallet balance
#             wallet = Wallet.objects.get(user=transaction.user)
#             wallet.balance += transaction.amount
#             wallet.save()
#         else:
#             transaction.status = Transaction.FAILED

#         transaction.save()
#         print(tx_ref, status)
#         # Return a successful response to Flutterwave
#         return HttpResponse('Success')


import os
import hashlib
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

@method_decorator(csrf_exempt, name='dispatch')
class Webhook(APIView):
    def post(self, request, format=None):
        secret_hash = settings.SECRET_HASH
        signature = request.headers.get("verifi-hash")
        if signature is None or signature != hashlib.sha256(secret_hash.encode('utf-8')).hexdigest():
            # This request isn't from Flutterwave; discard
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        payload = request.body
        # It's a good idea to log all received events.
        log(payload)
        # Do something (that doesn't take too long) with the payload
        return Response(status=status.HTTP_200_OK)



        



import requests
from rest_framework import generics, status
from rest_framework.response import Response



class WithdrawToBankAPIView(generics.CreateAPIView):
    serializer_class = BankAccountSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        bank_account = serializer.validated_data

        # Get bank code from Flutterwave API using bank name
        bank_name = bank_account['bank']
        response = requests.get(f'https://api.flutterwave.com/v3/banks',
                                headers={'Authorization': f'Bearer {settings.FLUTTERWAVE_SECRET_KEY}'})
        if response.status_code != 200:
            return Response({'message': 'Unable to get bank code.'}, status=status.HTTP_400_BAD_REQUEST)

        bank_data = response.json()['data'][0]
        bank_account['bank_code'] = bank_data['code']

        # Verify account name using Flutterwave API
        account_number = bank_account['account_number']
        response = requests.get(f'https://api.flutterwave.com/v3/accounts/resolve'
                                f'account_bank={bank_data["code"]}',
                                headers={'Authorization': f'Bearer {settings.FLUTTERWAVE_SECRET_KEY}'})
        if response.status_code != 200:
            return Response({'message': 'Unable to verify account name.'}, status=status.HTTP_400_BAD_REQUEST)

        account_data = response.json()['data']
        account_name = account_data['account_name']

        if account_name.lower() != bank_account['account_name'].lower():
            return Response({'message': 'Account name does not match.'}, status=status.HTTP_400_BAD_REQUEST)

        # Deduct transfer amount from user wallet
        user = self.request.user
        wallet = Wallet.objects.get(user=user)
        transfer_amount = bank_account['amount']
        if wallet.balance < transfer_amount:
            return Response({'message': 'Insufficient balance.'}, status=status.HTTP_400_BAD_REQUEST)

        wallet.balance -= transfer_amount
        wallet.save()

        # Initiate transfer to user bank account using Flutterwave API
        payload = {
            "account_bank": bank_account['bank_code'],
            "account_number": account_number,
            "amount": transfer_amount,
            "narration": "Wallet withdrawal to bank account",
            "currency": "NGN",
            "reference": f"wallet_to_bank_{user.id}"
        }

        response = requests.post('https://api.flutterwave.com/v3/transfers', json=payload,
                                 headers={'Authorization': f'Bearer {settings.FLUTTERWAVE_SECRET_KEY}'})
        if response.status_code == 200:
            return Response({'message': 'Transfer successful.'}, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'Unable to initiate transfer.'}, status=status.HTTP_400_BAD_REQUEST)


