from django.urls import path

from .views import ProfileView

urlpatterns = [
    path("profile/me/", ProfileView.as_view(), name="profile-me"),
]
