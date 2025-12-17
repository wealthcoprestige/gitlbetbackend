from django.db import models
from django.contrib.auth import get_user_model
from setup.basemodel import BaseModel

User = get_user_model()


# Create your models here.
class OpenTrade(BaseModel):
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    currency_pair = models.CharField(max_length=100)
    trade = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=22, decimal_places=2)

    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.currency_pair


class Transaction(BaseModel):
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=20, decimal_places=2)
    status = models.CharField(
        max_length=100,
        choices=[
            ("pending", "pending"),
            ("success", "success"),
            ("credited", "credited"),
            ("failed", "failed"),
        ],
    )
    transaction_type = models.CharField(
        max_length=100, choices=[("deposite", "deposite"), ("withdrawal", "withdrawal")]
    )
    address_wallet = models.CharField(max_length=255, null=True, blank=True)
    transaction_id = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f" {self.customer.username} Amount: {self.amount}"


class Investment(BaseModel):
    name = models.CharField(max_length=100)
    abbr = models.CharField(max_length=20)
    daily_earning = models.FloatField(default=0.00)
    amount = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    non_of_days = models.IntegerField(default=30)
    profit_return = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    roi = models.FloatField(default=0.00)
    hash_rate = models.FloatField(default=0.00)

    def __str__(self):
        return f"Name: {self.name} Amount: {self.amount}"


class CustomerInvestment(BaseModel):
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    investment = models.ForeignKey(Investment, on_delete=models.CASCADE)
    earnings = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    amount = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)

    is_active = models.BooleanField(default=False)

    def __str__(self):
        return f" {self.customer.username} earnings: {self.earnings}"


class PrestigeWealth(BaseModel):
    balance = models.DecimalField(decimal_places=2, max_digits=20)
    wallet_address = models.CharField(max_length=255) 

    def __str__(self):
        return self.wallet_address