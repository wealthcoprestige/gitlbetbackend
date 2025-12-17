from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from trade.serializers import *
from trade.models import *
import random
from django.shortcuts import get_object_or_404
from accounts.serializers import UserAccountSerializer
from rest_framework.exceptions import ValidationError


class OpenTradeAPIView(generics.GenericAPIView):
    serializer_class = OpenTradeSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save(customer=request.user, is_active=True)
            return Response({"message": "Trade Created Successfully"}, 201)
        return Response(serializer.errors, 400)


class CustomerInvestmentAPIView(generics.GenericAPIView):
    serializer_class = CustomerInvestmentSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        customer_investment = CustomerInvestment.objects.filter(
            customer=request.user, is_active=True
        )
        serializer = self.serializer_class(customer_investment, many=True)
        return Response({"data": serializer.data})


class InvestmentAPIView(generics.GenericAPIView):
    serializer_class = InvestmentSerializer
    permission_classes = [AllowAny]

    def get(self, request):
        investment = Investment.objects.all()
        serializer = self.serializer_class(investment, many=True)
        return Response({"data": serializer.data})


class CustomerTradesAPIView(generics.GenericAPIView):
    serializer_class = CustomerTradeSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        customer_trade = OpenTrade.objects.filter(customer=request.user, is_active=True)
        serializer = self.serializer_class(customer_trade, many=True)
        return Response({"data": serializer.data})


class WithdrawalAPIView(generics.GenericAPIView):
    serializer_class = WithdrawalSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            Transaction.objects.create(
                customer=request.user,
                amount=data["amount"],
                address_wallet=data["address_wallet"],
                status="pending",
                transaction_type="withdrawal",
                transaction_id=random.randint(10000000, 99999999),
            )
            return Response({"message": "Withdrawal request created successfully"}, 201)
        return Response(serializer.errors, 400)


class DepositeAPIView(generics.GenericAPIView):
    serializer_class = DepositeSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            Transaction.objects.create(
                customer=request.user,
                amount=data["amount"],
                status="pending",
                transaction_type="deposite",
                transaction_id=random.randint(10000000, 99999999),
            )
            return Response({"message": "Deposit request created successfully"}, 201)
        return Response(serializer.errors, 400)


class CustomerAccountAPIView(generics.GenericAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_prestige_wealth_address_wallet(self):
        return PrestigeWealth.objects.first()

    def get_customer_active_investment(self, customer):
        return CustomerInvestment.objects.filter(customer=customer, is_active=True)

    def get(self, request):
        user_transactions = Transaction.objects.filter(customer=request.user)

        deposits = self.serializer_class(
            user_transactions.filter(transaction_type="deposite"), many=True
        )
        withdrawals = self.serializer_class(
            user_transactions.filter(transaction_type="withdrawal"), many=True
        )
        customer = UserAccountSerializer(request.user)

        customer_investment = CustomerInvestmentSerializer(
            self.get_customer_active_investment(request.user), many=True
        )

        prestige_wealth= PrestigeWealthSerializer(self.get_prestige_wealth_address_wallet())

        return Response(
            {
                "deposite": deposits.data,
                "withdrawal": withdrawals.data,
                "customer": customer.data,
                "customer_investment": customer_investment.data,
                "prestige_wealth_address":prestige_wealth.data
            }
        )


class CreateCustomerInvestment(generics.CreateAPIView):
    serializer_class = CreateCustomerInvestmentSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        data = serializer.validated_data
        investment = data["investment"]

        if self.request.user.account_balance < investment.amount:
            
            raise ValidationError(
                {"message": "Insufficient Account Balance, Fund your account"}
            )
        self.request.user.account_balance -= investment.amount
        self.request.user.save()

        serializer.save(
            customer=self.request.user,
            is_active=True,
        )
