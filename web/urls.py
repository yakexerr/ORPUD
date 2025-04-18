from django.urls import path

from tasktracker import settings
from web.views import main_view, registration_view, auth_view, logout_view, time_slot_edit_view, tags_view, \
    tags_delete_view, holidays_view, holidays_delete_view

urlpatterns = [
    path("", main_view, name="main"),
    path("registration/", registration_view, name="registration"),
    path("auth/", auth_view, name="auth"),
    path("logout/", logout_view, name="logout"),
]
