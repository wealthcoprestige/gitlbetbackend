from django.urls import path
from .views import (
    OpenTradeAPIView,
    CustomerInvestmentAPIView,
    CustomerTradesAPIView,
    WithdrawalAPIView,
    DepositeAPIView,
    CustomerAccountAPIView,
    InvestmentAPIView,
    CreateCustomerInvestment
)

urlpatterns = [
    path('open-trade/', OpenTradeAPIView.as_view(), name='open-trade'),
    path('customer/investments/', CustomerInvestmentAPIView.as_view(), name='customer-investments'),
    path('trades/', CustomerTradesAPIView.as_view(), name='customer-trades'),
    path('withdrawal/', WithdrawalAPIView.as_view(), name='withdrawal'),
    path('deposit/', DepositeAPIView.as_view(), name='deposit'),
    path('customer/account/', CustomerAccountAPIView.as_view(), name='transactions'),
    path('investment/', InvestmentAPIView.as_view(), name='investment'),
    path('create/customer/investment/', CreateCustomerInvestment.as_view(), name='create_customer_investment')
]
