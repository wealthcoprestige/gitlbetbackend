# Django imports
from django.contrib.auth.models import AbstractBaseUser
from .base_manager import MyAccountManager
from django.db import models
import uuid
from setup.basemodel import BaseModel
from datetime import datetime
from django.utils import timezone
from general.random_vals import get_random_nums

# UTILITY MODELS

class Country(BaseModel):
    name = models.CharField(max_length=255)
    emoji_icon = models.CharField(max_length=100)
    abbr = models.CharField(max_length=10)
    phone_code = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.name} ({self.abbr})"

    class Meta:
        ordering = ["name"]

# - locations
class City(BaseModel):
    name = models.CharField(
        max_length=100,
        unique=True,
        blank=True,
        null=True,
        help_text="eg. Kumasi, Accra etc",
    )

    class Meta:
        verbose_name_plural = "Cities"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Town(BaseModel):
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    name = models.CharField(
        max_length=100, help_text="eg. Nkoransah, Santasi, Adum etc"
    )
    lat = models.CharField(max_length=50, blank=True, null=True)
    lon = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        unique_together = ("city", "name")
        ordering = ["name"]
        verbose_name_plural = "Towns"

    def __str__(self):
        return f"{self.name} - {self.city}"


# USER BASIC MODELS
class User(AbstractBaseUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    on_android = models.BooleanField(default=False)
    on_ios = models.BooleanField(default=False)

    photo = models.ImageField(upload_to="profile_photos/", blank=True, null=True)
    username = models.CharField(max_length=100, null=True, blank=True)
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)

    email = models.EmailField(unique=True, blank=True, null=True)
    phone_number = models.CharField(max_length=10, unique=True)

    town = models.ForeignKey(Town, blank=True, null=True, on_delete=models.SET_NULL)
    street_address = models.CharField(max_length=150, blank=True, null=True)
    digital_address = models.CharField(
        max_length=20, blank=True, null=True, help_text="Enter Ghana digital address"
    )
    country = models.ForeignKey(
        Country, on_delete=models.SET_NULL, blank=True, null=True
    )
    gender = models.CharField(
        max_length=10,
        choices=[("Male", "Male"), ("Female", "Female")],
        blank=True,
        null=True,
    )
    date_of_birth = models.DateField(blank=True, null=True)

    referral_code = models.CharField(max_length=50, blank=True, null=True, unique=True)
    referred_by = models.CharField(max_length=50, blank=True, null=True)

    account_balance = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)

    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(verbose_name="date joined", auto_now_add=True)
    last_login = models.DateTimeField(verbose_name="last joined", auto_now=True)
    last_seen = models.DateTimeField(verbose_name="last seen", blank=True, null=True)

    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = MyAccountManager()

    USERNAME_FIELD = "phone_number"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name_plural = "Users"
        ordering = ["first_name"]

    def __str__(self):
        if self.first_name:
            return self.get_full_name()
        return self.phone_number

    def get_full_name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name.capitalize()} {self.last_name.capitalize()}"
        return self.first_name or "Anonymous"

    def initials(self):
        if self.first_name and self.last_name:
            return f"{(self.first_name[0] + self.last_name[0]).upper()}"
        return self.email[0].upper()

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return True

    def age(self):
        from datetime import date

        if self.date_of_birth:
            return date.today().year - self.date_of_birth.year
        return None

    def set_fcm_token(self, token):
        self.fcm_token = token
        self.save()

    def get_fcm_token(self):
        return self.fcm_token


class UserVerificationCode(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    mail_code = models.CharField(max_length=6, null=True, blank=True)
    phone_code = models.CharField(max_length=6, null=True, blank=True)
    mail_verified = models.BooleanField(default=False)
    phone_verified = models.BooleanField(default=False)
    mail_code_expires = models.DateTimeField(default=datetime.utcnow)
    phone_code_expires = models.DateTimeField(default=datetime.utcnow)

    def __str__(self):
        return f"{self.user.phone_number} (code)"

    def save(self, *args, **kwargs):
        if not self.mail_code or not self.phone_code:
            self.mail_code = get_random_nums(6)
            self.phone_code = get_random_nums(6)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "Verification Codes"
        ordering = ["created_at"]

    # codes expiration
    def is_expired_mail_code(self):
        return datetime.utcnow().hour > self.mail_code_expires.hour + 2

    def is_expired_phone_code(self):
        return datetime.utcnow().hour > self.phone_code_expires.hour + 2

    # codes duration
    def get_mail_code_duration(self):
        current_hour = datetime.utcnow().hour
        expired_hour = self.mail_code.hour
        return current_hour - 3 > expired_hour

    def get_phone_code_duration(self):
        current_hour = datetime.utcnow().hour
        expired_hour = self.phone_code.hour
        return current_hour - 3 > expired_hour


class LoggedInUserDevices(BaseModel):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="logged_in_user_user"
    )
    ip_address = models.GenericIPAddressField()
    os = models.CharField(max_length=255)
    browser = models.CharField(max_length=255)
    expires = models.DateTimeField(default=datetime.utcnow)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.get_full_name()}-{self.ip_address}"

    def is_refresh_token_expired(self):
        return datetime.utcnow().day >= self.created_at.day + 1

    class Meta:
        ordering = ["-created_at"]


# App configs
class AppSettings(models.Model):
    # General Info
    app_name = models.CharField(max_length=100, default="Wealth Tok")
    support_email = models.EmailField(default="info.finvib@gmail.com")
    support_phone = models.CharField(max_length=20, blank=True, null=True)

    # Push Notification Settings
    fcm_access_token = models.TextField(blank=True, null=True)
    fcm_access_token_expires_at = models.DateTimeField(blank=True, null=True)
    notification_enabled = models.BooleanField(default=True)

    # Feature Toggles
    enable_chat = models.BooleanField(default=True)
    enable_payments = models.BooleanField(default=True)

    # App Behavior
    default_timezone = models.CharField(max_length=50, default="UTC")
    maintenance_mode = models.BooleanField(default=False)
    maintenance_message = models.TextField(blank=True, null=True)

    # Branding & Links
    primary_color = models.CharField(max_length=7, default="#E92929")  # HEX color
    secondary_color = models.CharField(max_length=7, default="#FFFFFF")
    terms_url = models.URLField(blank=True, null=True)
    privacy_url = models.URLField(blank=True, null=True)

    # Audit
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "App Settings"
        verbose_name_plural = "App Settings"

    def save(self, *args, **kwargs):
        # Ensure only one settings record exists
        if not self.id and AppSettings.objects.exists():
            raise ValueError("Only one AppSettings instance allowed.")
        super().save(*args, **kwargs)

    @classmethod
    def get_instance(cls):
        obj, _ = cls.objects.get_or_create(defaults={})
        return obj

    def __str__(self):
        return "App Settings"
