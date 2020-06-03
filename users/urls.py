from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, \
    PasswordResetCompleteView
from django.urls import path

urlpatterns = [
    path('password/reset/', PasswordResetView.as_view(template_name='users/password_reset_form.html',
                                                      html_email_template_name='users/password_reset_email.html',
                                                      subject_template_name="users/password_reset_subject.txt"),
         name='password_reset'),
    path('password/reset/done', PasswordResetDoneView.as_view(template_name='users/password_reset_done.html'),
         name='password_reset_done'),
    path('password/reset/<uidb64>/<token>/',
         PasswordResetConfirmView.as_view(template_name='users/password_reset_confirm.html'),
         name='password_reset_confirm'),
    path('password/reset/complete',
         PasswordResetCompleteView.as_view(template_name='users/password_reset_complete.html'),
         name='password_reset_complete'),
]
