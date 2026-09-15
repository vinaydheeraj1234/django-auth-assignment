import secrets
from datetime import timedelta

from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import generics, status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import EmailOTP
from .serializers import (
    LoginSerializer,
    RegisterSerializer,
    UserSerializer,
    VerifyOTPSerializer,
)

OTP_VALID_MINUTES = 10


class RegisterView(generics.GenericAPIView):
    serializer_class = RegisterSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]

        # if user registered before but did not verify, use the same user again
        user = User.objects.filter(username=email).first()
        if user is None:
            user = User(username=email, email=email)
        user.set_password(password)
        user.is_active = False  # user can not login until otp is verified
        user.save()

        otp = f"{secrets.randbelow(1000000):06d}"
        EmailOTP.objects.update_or_create(user=user, defaults={"code": otp})

        send_mail(
            "Your OTP for registration",
            f"Your OTP is {otp}. It is valid for {OTP_VALID_MINUTES} minutes.",
            settings.DEFAULT_FROM_EMAIL,
            [email],
        )

        return Response(
            {"message": "OTP sent to your email. Please verify to complete registration."},
            status=status.HTTP_201_CREATED,
        )


class VerifyOTPView(generics.GenericAPIView):
    serializer_class = VerifyOTPSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"].lower()
        code = serializer.validated_data["otp"]

        otp = EmailOTP.objects.filter(user__username=email).first()
        if otp is None or otp.code != code:
            return Response({"error": "Invalid OTP."}, status=status.HTTP_400_BAD_REQUEST)

        if timezone.now() - otp.created_at > timedelta(minutes=OTP_VALID_MINUTES):
            otp.delete()
            return Response(
                {"error": "OTP expired. Please register again."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = otp.user
        user.is_active = True
        user.save()
        otp.delete()

        return Response({"message": "Registration successful. You can login now."})
    
class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"].lower()
        password = serializer.validated_data["password"]

        # authenticate gives None if password is wrong or user is not active
        user = authenticate(request, username=email, password=password)
        if user is None:
            return Response(
                {"error": "Invalid email or password."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        user.last_login = timezone.now()
        user.save(update_fields=["last_login"])

        # delete old token and create a new one on every login
        Token.objects.filter(user=user).delete()
        token = Token.objects.create(user=user)

        response = Response({"message": "Login successful."})
        response.set_cookie(
            "auth_token",
            token.key,
            max_age=60 * 60 * 24,  # 1 day
            httponly=True,  # javascript can not read this cookie
            secure=True,  # only sent over https (browsers allow localhost)
            samesite="Lax",
        )
        return response
    

class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # delete the token from database so old cookie stops working
        request.auth.delete()

        response = Response({"message": "Logged out successfully."})
        response.delete_cookie("auth_token", samesite="Lax")
        return response