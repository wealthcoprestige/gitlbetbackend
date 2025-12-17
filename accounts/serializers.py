from rest_framework import serializers
from accounts.models import *
from django.contrib.auth import get_user_model


User = get_user_model()


    
class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = "__all__"

class CitySerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)
    class Meta:
        model = City
        fields = "__all__"

class TownSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)
    city = serializers.CharField(source='city.id', read_only=True)
    class Meta:
        model = Town
        fields = "__all__"

        
        
# USER SERIALIZERS
class UserSerializer(serializers.ModelSerializer):
    town = TownSerializer()
    class Meta:
        model = User
        exclude = ["password", "is_admin", "is_staff", "is_superuser", 'account_balance']
        read_only_fields = ['is_active']


class UserAccountSerializer(serializers.ModelSerializer):
    town = TownSerializer()
    class Meta:
        model = User
        exclude = ["password", "is_admin", "is_staff", "is_superuser"]
        read_only_fields = ['is_active']


class UserVerificationCodeSerializer(serializers.ModelSerializer):
    """
    Strictly private serializer
    Not to be used in VIEWS
    """
    user = UserSerializer()
    class Meta:
        model = UserVerificationCode
        exclude = ["mail_verified", "phone_verified"]



class UserMailVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        try:
            User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError('User with this email does not exist')
        return value


class UserPhoneVerificationSerializer(serializers.Serializer):
    phone = serializers.CharField()

    def validate(self, data):
        if not User.objects.filter(phone_number=data.get("phone")).exists():
            raise serializers.ValidationError('Not found')
        return data
    

class CreateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "phone_number",
            "password"
        ]

    def create(self, validated_data):
        password = validated_data.get("password")
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user

# Login Serializers
class EmailLoginUserSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)


class PhoneLoginUserSerializer(serializers.Serializer):
    phone = serializers.CharField(required=True)
    password = serializers.CharField(required=True)


class LogoutSerializer(serializers.Serializer):
    refresh_token = serializers.CharField(max_length=255)


# Reset serializers
class PasswordResetSetPasswordSerializer(serializers.Serializer):
    phone = serializers.CharField(required=True)
    password = serializers.CharField(required=True)

    def validate_password(self, password):
        if len(password) < 8:
            raise serializers.ValidationError(
                "Password must be 8 digits or more"
            )
        # # check for small letters
        # if not any(char.islower() for char in password):
        #     raise serializers.ValidationError(
        #         "Weak password, Must contain at least one small letter"
        #     )

        # # check for capital letters
        # if not any(char.isupper() for char in password):
        #     raise serializers.ValidationError(
        #         "Weak password, Must contain at least one capital letter"
        #     )

        # # check for numbers
        # if not any(char.isdigit() for char in password):
        #     raise serializers.ValidationError(
        #         "Weak password, Must contain at least one number"
        #     )

        # # check for characters
        # if not any(char.isascii() for char in password):
        #     raise serializers.ValidationError(
        #         "Weak password, Must contain at least one character"
        #     )

        return password


class PasswordResetSerializer(serializers.Serializer):
    phone = serializers.CharField()

#  Verify serializers
class UserVerifyEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    code = serializers.CharField(required=True)

    def validate_code(self, code):
        if not code.isdigit():
            raise serializers.ValidationError(
                "Bad request"
            )
        return code
    
class UserVerifyPhoneSerializer(serializers.Serializer):
    phone = serializers.CharField(required=True)
    code = serializers.CharField(required=True)

    def validate_code(self, code):
        if not code.isdigit():
            raise serializers.ValidationError(
                "Bad request"
            )
        return code