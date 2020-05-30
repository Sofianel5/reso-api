from django.contrib.auth import views as auth_views
from django.urls import path, include
from . import views
from . import forms

urlpatterns = [
    path("signup/", views.signup, name="signup"),
    path("signin/", auth_views.LoginView.as_view(template_name='ecommerce/signin.html', authentication_form=forms.SignInForm), name="signin"),
    path("signout/", auth_views.LogoutView.as_view(), name="users/signout"),
    path("", views.home, name="home"),
    path("subscriptions/", views.choose_subscription, name="subscriptions"),
    path("checkout/", views.subscribe, name="checkout"),
    path("team/", views.team, name="our_team"),
    path("enterprise/", views.enterprise, name="enterprise"),
    path("success/", views.success, name="success"),
]