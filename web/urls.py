from django.urls import path

from tasktracker import settings
from web.views import *

urlpatterns = [
    path("", main_view, name="main"),
    path("registration/", registration_view, name="registration"),
    path("auth/", auth_view, name="auth"),
    path("logout/", logout_view, name="logout"),
    path("project/", project_view, name="project"),
    path("profile/", profile_view, name="profile"),
    path("employees_dashboard/", employees_dashboard_view, name="employees_dashboard"),
    path("projects_dashboard/", projects_dashboard_view, name="projects_dashboard"),
    path("calendar/", calendar_view, name="calendar"),
    path("feedback/", feedback_view, name="feedback"),
    path("tasks/add/", add_task_view, name="add_task"),
    path("employees/add/", add_employee_view, name="add_employee"),
    path("tags", task_tags_view, name="tags"),
    path("tags/<int:id>/delete/", delete_task_tag_view, name="delete_tag"),
    # TODO: Переделать формочки под models.py
    # path("time_slots/add/", time_slot_edit_view, name="time_slots_add"),
    # path("time_slots/<int:id>/", time_slot_edit_view, name="time_slots_edit"),
    # path("tags/", tags_view, name="tags"),
    # path("tags/<int:id>/delete/", tags_delete_view, name="tags_delete"),
    # path("holidays/", holidays_view, name="holidays"),
    # path("holidays/<int:id>/delete/", holidays_delete_view, name="holidays_delete"),

]
