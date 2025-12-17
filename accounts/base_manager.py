from django.contrib.auth.models import BaseUserManager

class MyAccountManager(BaseUserManager):
    def create_superuser(self, phone_number, email=None, password=None):
        user = self.create_user(phone_number, email, password)
        user.is_superuser = True
        user.is_admin = True
        user.is_active = True
        user.is_staff = True
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, phone_number, email=None, password=None):
        if not phone_number:
            raise ValueError("Users must have an phone number.")
        if email and "@" not in email and ".com" not in email:
            raise ValueError("Invalid email input")
        if len(password) < 8:
            raise ValueError("Password 8 must contain at least 8 characters")

        user = self.model(phone_number=phone_number)
        user.email = email
        user.set_password(password)
        user.save(using=self._db)
        return user