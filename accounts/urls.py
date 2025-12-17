from django.urls import path
from accounts.views import *


urlpatterns = [
    path('create-user/', CreateUserView.as_view(), name='create-user'),
    path('login-user-phone/', LoginUserView.as_view(), name='login-user-phone')
]