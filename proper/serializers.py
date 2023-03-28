from rest_framework import serializers

from .models import *

from django.urls import reverse

# class PropertySerializer(serializers.ModelSerializer):
    
#     class Meta:
#         model = Property
#         fields = '__all__'

# class PropertySerializer(serializers.ModelSerializer):
#     buy_url = serializers.SerializerMethodField()

#     class Meta:
#         model = Property
#         fields = ('id', 'property_name', 'location', 'amount', 'category', 'description', 'price_per_slot', 'roi', 'duration', 'slots_available', 'terms_and_condition', 'pictures', 'buy_url')

#     def get_buy_url(self, obj):
#         request = self.context.get('request')
#         if request is not None:
#             url = reverse('buy', kwargs={'product_id': obj.id})
#             return request.build_absolute_uri(url)


class PropertySerializer(serializers.ModelSerializer):
    buy_url = serializers.SerializerMethodField()
    # owner = serializers.HiddenField(default=serializers.CurrentUserDefault())
    # pictures = ImageSerializer(many=True)

    class Meta:
        model = Property
        fields = ('id',  'user', 'property_name', 'location', 'amount', 'category', 'description', 'price_per_slot', 'roi', 'duration', 'slots_available', 'terms_and_condition', 'image1', 'image2',  'image3', 'buy_url')
        read_only_fields = ('id', 'user')

    def get_buy_url(self, obj):
        request = self.context.get('request')
        if request is not None:
            url = reverse('buy', kwargs={'product_id': obj.id})
            return request.build_absolute_uri(url)

    # def create(self, validated_data):
    #     validated_data['owner'] = self.context['request'].user
    #     return super().create(validated_data)


# class AdminPropertySerializer(serializers.ModelSerializer):
#     # buy_url = serializers.SerializerMethodField()
#     # pictures = ImageSerializer(many=True)

#     class Meta:
#         model = AdminUserProperty
#         fields = ('id',  'user', 'property_name', 'location', 'amount', 'category', 'description', 'price_per_slot', 'roi', 'duration', 'slots_available', 'terms_and_condition', 'image1', 'image2',  'image3',)
#         read_only_fields = ('id', 'user')

    

   

class InvestmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Investment
        fields = '__all__'
        read_only_fields = ('id', 'user', 'product', 'current_value', 'start_date', 'end_date')


class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = '__all__'


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ('amount',)


class BankAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankAccount
        fields = ('account_number', 'bank', 'amount')
        read_only_fields = ('id', 'user', 'created_at', 'updated_at')
        