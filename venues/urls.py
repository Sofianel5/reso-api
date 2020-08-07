from django.urls import path, include
from django.views.generic.base import TemplateView
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from . import views

urlpatterns = [
    path("share/", views.venue_preview, name="share-venue")
]