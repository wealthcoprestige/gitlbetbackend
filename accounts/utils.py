from rest_framework_simplejwt.tokens import RefreshToken
from general.random_vals import get_random_nums
from django.contrib.auth import get_user_model
from .models import UserVerificationCode
from django.db import transaction
from django.utils import timezone
from datetime import timedelta


User = get_user_model()

class AppUtil:
    def get_user_from_refresh_token(refresh_token):
        try:
            refresh_token = RefreshToken(refresh_token)
            user_id = refresh_token.payload.get('user_id')
            user = User.objects.get(id=user_id)
            return user
        except Exception as e:
            return None

''''
 A class in charge of creating verification codes through mail
 and phone
'''
class UserVerificationUtil:

    @transaction.atomic
    def create_and_send_email_code(email):
        user_code, _ = UserVerificationCode.objects.get_or_create(
            user = User.objects.get(email=email)
        )
        user_code.mail_code = get_random_nums(5)
        user_code.save()
        # send


    @transaction.atomic
    def create_phone_code(phone):
        user_code, _ = UserVerificationCode.objects.get_or_create(
            user = User.objects.get(phone_number=phone)
        )
        if not _ and user_code.updated_at > timezone.now() - timedelta(minutes=20):
            print("Code was recently sent. Not resending.")
            return

        user_code.phone_code = get_random_nums(5)
        user_code.save()
        # send
        AuthenticationSMS.send_verification_code_to_phone(
            user_code = user_code.phone_code, 
            user_phone_number = phone
        )


class VerificationCodeUtil:

    def get_verification_code_by_email(email, code):
        try:
            code = UserVerificationCode.objects.get(
                user__email=email, mail_code=code
            )
            user = User.objects.get(email=email)
            user.is_active = True 
            user.save()

            code.mail_verified = True 
            code.save()
            return True
        except Exception:
            return False

    def get_verification_code_by_phone(phone:str, code):
        try:
            code = UserVerificationCode.objects.get(
                user__phone_number = phone,
                phone_code=code
            )
            user = User.objects.get(phone_number = phone)
            user.is_active = True 
            user.save()

            code.phone_verified = True
            code.save()
            return True
        except Exception:
            return False 