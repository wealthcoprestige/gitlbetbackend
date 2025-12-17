from rest_framework import serializers
from accounts.serializers import UserSerializer
from trade.models import *


class OpenTradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = OpenTrade
        fields = ['currency_pair', 'trade', 'amount']


class WithdrawalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['amount', 'address_wallet']


class DepositeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['amount']


class CreateCustomerInvestmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerInvestment
        fields = ['investment', 'amount']





class CreateCustomerInvestmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerInvestment
        exclude = ['earnings', 'is_active']


class InvestmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Investment
        fields = "__all__"


class CustomerInvestmentSerializer(serializers.ModelSerializer):
    investment = InvestmentSerializer()
    class Meta:
        model = CustomerInvestment
        fields = "__all__"


class CustomerTradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = OpenTrade
        fields = "__all__"


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = "__all__"


class PrestigeWealthSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrestigeWealth
        exclude = ['balance']
