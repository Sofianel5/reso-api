from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path("auth/", include('djoser.urls')),
    path("auth/", include("djoser.urls.authtoken")),
    path("venues/", views.VenueList.as_view()),
    path("venues/<int:pk>/", views.VenueDetail.as_view()),
    path("me/", views.CustomUserUpdate.as_view()),
    path("venues/<int:pk>/timeslots/", views.TimeSlotManager.as_view()),
    path("venues/<int:venue>/register/<int:timeslot>/", views.TimeSlotRegistration.as_view()),
    path("venues/search/", views.VenueSearch.as_view()),
    path("me/toogle-lock/", views.ToggleLockState.as_view()),
    path("me/scan/", views.UserScanManager.as_view()),
    path("venues/<int:pk>/scan/", views.VenueScanManager.as_view()),
    path("me/registrations/", views.UserBookingsManager.as_view()),
    path("fixtures/", views.Fixture.as_view()),
    path("myadmin/", views.VenueAdminLogin.as_view()),
    path("myadmin/venues/<int:venue>/timeslots/", views.VenueAdminTimeSlotInfo.as_view()),
]

