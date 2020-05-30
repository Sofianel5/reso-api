from django.contrib.auth import views as auth_views
from django.urls import path, include
from .views import *

urlpatterns = [
    path("signup/", auth_views.signup, name="signup"),
    path("signin/", auth_views.LoginView.as_view(template_name='ecommerce/signin.html'), name="signin"),
    path("signout/", auth_views.LogoutView.as_view(), name="users/signout"),
    path("home/", home, name="home")
]