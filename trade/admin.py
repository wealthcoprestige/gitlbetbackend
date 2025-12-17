from django.contrib import admin
from trade.models import *
# Register your models here.


admin.site.register(OpenTrade)
admin.site.register(Transaction)
admin.site.register(Investment)
admin.site.register(CustomerInvestment)
admin.site.register(PrestigeWealth)