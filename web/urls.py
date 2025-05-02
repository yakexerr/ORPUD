from django.urls import path

from tasktracker import settings
from web.views import *

urlpatterns = [
    path("", main_view, name="main"),
    path("registration/", registration_view, name="registration"),
    path("auth/", auth_view, name="auth"),
    path("logout/", logout_view, name="logout"),
    path("action_message/", action_message_view, name="action_message"),
    path("project/", first_project_redirect_view.as_view(), name="project"),
    path("project/<int:id>/complete", complete_project_view, name="complete_project"),
    path("project/<int:id>/", project_view, name="current_project"),
    path("project/<int:id>/edit/", edit_project_view, name="edit_project"),
    path("project/<int:id>/delete/", delete_project_view, name="delete_project"),
    path("project/add/", edit_project_view, name="add_project"),
    path("project/all", projects_view, name="projects"),
    path("profile/", profile_view, name="my_profile"),
    path("profile/<int:id>/", profile_view, name="other_profile"),
    path("profile/edit", edit_profile_view, name="edit_profile"),
    path("profile/delete", delete_profile_view, name="delete_profile"),
    path("employees_dashboard/", employees_dashboard_view, name="employees_dashboard"),
    path("projects_dashboard/", projects_dashboard_view, name="projects_dashboard"),
    path("calendar/", calendar_view, name="calendar"),
    path("feedback/", feedback_view, name="feedback"),
    path("tasks/add/", edit_task_view, name="add_task"),
    path("tasks/<int:id>/edit/", edit_task_view, name="edit_task"),
    path("tasks/<int:id>/delete/", delete_task_view, name="delete_task"),
    path("tasks/<int:id>/complete/", complete_task_view, name="complete_task"),
    path("tags", task_tags_view, name="tags"),
    path("tags/<int:id>/delete/", delete_task_tag_view, name="delete_tag"),
    path("task/<int:id>/", current_task_view, name="current_task"), #для теста
    path("tasks/", task_view, name="tasks"),
    path("tasks/completed/", completed_task_view, name="completed_tasks"),#для теста
    path("employees/", employees_view, name="employees"),
    path("employees/add/", edit_employee_view, name="add_employee"),
    path("employees/<int:id>/edit/", edit_employee_view, name="edit_employee"),
    path("employees/<int:id>/delete", delete_employee_view, name="delete_employee"),
]
