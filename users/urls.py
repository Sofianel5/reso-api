from django.contrib.auth import views as auth_views
from django.conf.urls import url

urlpatterns = [
    url('^', include('django.contrib.auth.urls')),
]