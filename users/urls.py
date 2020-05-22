from django.urls import path, include
from django.views.generic.base import TemplateView
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView

urlpatterns = [
    path('/password/reset/', PasswordResetView.as_view(template_name='users/password_reset_form.html'), name='password_reset'),
    path('/password/reset/', PasswordResetDoneView.as_view(template_name='regisuserstration/password_reset_done.html'), name='password_reset_done'),
    path('/password/reset/', PasswordResetConfirmView.as_view(template_name='users/password_reset_confirm.html'), name='password_reset_confirm'),
    path('/password/reset/', PasswordResetCompleteView.as_view(template_name='users/password_reset_comlete.html'), name='password_reset_complete'),
]