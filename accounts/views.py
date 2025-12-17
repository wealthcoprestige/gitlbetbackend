# django/python imports
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import generics, views
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

# local app imports
from rest_framework.throttling import AnonRateThrottle
from accounts.models import User, UserVerificationCode
from .serializers import *
from .middlewares import UserMiddlewares
from .utils import UserVerificationUtil, VerificationCodeUtil, AppUtil
from accounts.serializers import UserSerializer


class CreateUserView(generics.GenericAPIView):
	serializer_class = CreateUserSerializer
	permission_classes = [AllowAny]

	def post(self, request):
		try:
			serializer = self.serializer_class(data=request.data)
			if serializer.is_valid(raise_exception=True):
				user = serializer.save()
				
				return Response({"message": "Account created successfully"}, status=201)
			return Response({"message": "Bad request"}, status=400)
		except Exception as e:
			return Response({"message": "Internal server error"}, status=500)
		

class UserVerificationView(generics.GenericAPIView):
	serializer_class = UserPhoneVerificationSerializer
	serializers_classes = {
		"email": UserMailVerificationSerializer,
		"phone": UserPhoneVerificationSerializer,
	}
	permission_classes = [AllowAny]

	def get_query_param(self):
		params = self.request.query_params
		email = params.get("email")
		phone = params.get("phone")
		return email if email == "email" else phone if phone == "phone" else ""

	def post(self, request):
		channel = self.get_query_param()
		if channel == "email":
			data = self.serializers_classes["email"](data=request.data)
			data.is_valid(raise_exception=True)
			UserVerificationUtil.create_and_send_email_code(data.data.get("email"))
			return Response({"message": "Verification code sent to email"}, status=201)
		elif channel == "phone":
			data = self.serializers_classes["phone"](data=request.data)
			data.is_valid(raise_exception=True)
			UserVerificationUtil.create_phone_code(
				phone = data.data.get("phone")
			)
			return Response({"message": "Verification code sent to phone"}, status=201)
		else:
			return Response({"message": "Not found"}, status=404)



class LoginUserView(generics.GenericAPIView, UserMiddlewares):
	permission_classes = [AllowAny]
	serializer_class = PhoneLoginUserSerializer
	serializer_classes = {
		"email": EmailLoginUserSerializer,
		"phone": serializer_class, 
	}
	login_failed_body = {
		"message": "Please enter the correct {method} and password. Note that both fields may be case-sensitive"
	}

	def custom_authenticate_user(self, user) -> dict:
		token = RefreshToken.for_user(user)
		self.get_save_user_device(self.request, user)
		data = {
				"message": "Login successful",
				"user": self.user_serializer(user).data,
				"tokens": [
					{
						"access_token": str(token.access_token),
						"refresh_token": str(token)
					}
				],
			}
		
		
		return data
		
	def get_query_param(self) -> str:
		params = self.request.query_params
		email = params.get("email")
		phone = params.get("phone")
		return email if email == "email" else phone if phone == "phone" else ""

	def post(self, request):
		login_method = self.get_query_param()
		if login_method:
			data = self.serializer_classes.get(login_method)(data=request.data)
			data.is_valid(raise_exception=True) 
			data = data.data

		if login_method == "email":
			user = self.get_user_by_email(email=data.get("email"), password=data.get("password"))
			if user == None:
				return Response({"error": "Email not verified"}, 401)
			elif user == False:
				return Response(self.login_failed_body['message'].format(method="email"), 404)
			return Response(self.custom_authenticate_user(user), 200) if user else Response(self.login_failed_body, status=404)
		
		elif login_method == "phone":
			user = self.get_user_by_phone(phone=data.get("phone"), password=data.get("password"))
			
			if user == None:
				return Response({"error": "Phone not verified"}, 401)
			elif user == False:
				return Response(self.login_failed_body['message'].format(method="phone number"), 404)
			return Response(self.custom_authenticate_user(user), 200) if user else Response(self.login_failed_body, status=404)
		else:
			return Response({"error": "Bad request"}, status=403)


class RefreshTokenSerializerView(views.APIView):
	permission_classes = [AllowAny]

	def custom_authenticate_user(self, user) -> dict:
		token = RefreshToken.for_user(user)
		data = {
				"message": "Token refreshed!",
				"user": UserSerializer(user).data,
				"tokens": [
					{
						"access_token": str(token.access_token),
						"refresh_token": str(token),
					}
				],
			}
		return data

	def get(self, request, refresh_token):
		user = AppUtil.get_user_from_refresh_token(refresh_token)
		if user:
			return Response(self.custom_authenticate_user(user))
		return Response({"message":"Failed!"}, 404)


class LogoutView(generics.GenericAPIView, UserMiddlewares):
	permission_classes = [AllowAny]
	serializer_class = LogoutSerializer

	def post(self, request):
		data = self.serializer_class(data=request.data)
		data.is_valid(raise_exception=True)
		validated_data = data.data
		try:
			self.logout_user_device(request)
			# Blacklist token
			token = RefreshToken(validated_data["refresh_token"])
			token.blacklist()
			return Response("Successful Logout", 200)
		except Exception as e:
			return Response(str(e), 400)


class PasswordResetRequestCodeView(generics.GenericAPIView):
	serializer_class = PasswordResetSerializer
	permission_classes = [AllowAny]
	throttle_classes = [AnonRateThrottle]

	def post(self, request):
		data = self.serializer_class(data=request.data)
		data.is_valid(raise_exception=True)
		validated_data = data.data

		if User.objects.filter(phone_number=validated_data["phone"]).exists():
			# Get user
			user = User.objects.get(phone_number=validated_data["phone"])
			# Clear all old verification codes if exist
			verify_codes = UserVerificationCode.objects.filter(user=user)
			verify_instance = verify_codes.first() 
			phone_verified = True if verify_instance and verify_instance.phone_verified == True else False
			mail_verified = True if verify_instance and verify_instance.mail_verified == True else False
			
			if verify_instance.is_expired_phone_code():
				verify_codes.delete()
			else:
				return Response({
					"message": "Code already sent and is active"
				}, status=201)

			code = UserVerificationCode.objects.create(user=user, phone_verified=phone_verified, mail_verified=mail_verified)
			

			return Response(
				{"message": "Password reset code has been sent to your phone"},
				status=201
			)
		return Response({"message": "User phone does not exist"}, 404)


class PasswordResetView(generics.GenericAPIView):
	permission_classes = [AllowAny]
	serializer_class = PasswordResetSetPasswordSerializer

	def get(self, request, code):
		verify_code = get_object_or_404(UserVerificationCode, code=code)
		if verify_code and not verify_code.is_expired():
			return Response({"message": "Code valid"})
		return Response({"message": "Invalid code"}, 404)

	def post(self, request, code):
		data = self.serializer_class(data=request.data)
		data.is_valid(raise_exception=True)
		validated_data = data.data
		# Get verification code obj
		verify_code = get_object_or_404(UserVerificationCode, user__phone_number=validated_data.get('phone'), phone_code=code)
		if verify_code and not verify_code.is_expired_phone_code():
			
			user = User.objects.get(phone_number=validated_data['phone'])
			user.set_password(validated_data["password"])
			user.save()
			return Response({"message": "Password reset successful"}, status=201)
		return Response({"message": "Invalid or expired code provided"}, 400)


class CountryView(generics.GenericAPIView):
	serializer_class = CountrySerializer
	permission_classes = [AllowAny]

	def get(self, request):
		countries = Country.objects.all()
		data = self.serializer_class(countries, many=True).data
		return Response({'data': data})



