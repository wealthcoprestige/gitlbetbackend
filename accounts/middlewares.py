from django.contrib.auth import get_user_model

from accounts.models import LoggedInUserDevices, UserVerificationCode
from general.ip_address import get_user_ip_address
from .serializers import UserSerializer

User = get_user_model()


class UserMiddlewares:
    user_serializer = UserSerializer

    def get_user_by_email(self, email, password):
        # Check against email and password
        try:
            user = User.objects.get(email=email)

            user_email_verified_check = UserVerificationCode.objects.filter(
                user__email=email, 
                mail_verified=True).exists()
            if not user_email_verified_check:
                return None
            
            return user if user.check_password(password) and user_email_verified_check else False
        except Exception:
            return False
        
    def get_user_by_phone(self, phone, password):
        # Check against phone and password
        try:
            user = User.objects.get(phone_number=phone)

            # user_phone_verified_check = UserVerificationCode.objects.filter(
            #     user__phone_number=phone, 
            #     phone_verified=True).exists()
            # if not user_phone_verified_check:
            #     return None
            
            return user if user.check_password(password) else False
        except Exception:
            return False

    def get_save_user_device(self, request, user):
        LoggedInUserDevices.objects.create(
            user=user,
            ip_address=get_user_ip_address(request),
            browser=request.user_agent.browser.family,
            os=request.user_agent.os,
        )

    def logout_user_device(self, request):
        LoggedInUserDevices.objects.filter(
            ip_address=get_user_ip_address(request), is_active=True
        ).update(is_active=False)