from django.urls import path

from . import views

urlpatterns = [
    path("register/", views.RegisterView.as_view(), name="register"),
    path("register/verify/", views.VerifyOTPView.as_view(), name="register-verify"),
]