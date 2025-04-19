from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.template.context_processors import request
from web.models import Task, EmployeeAccount, TaskTag
from web.forms import RegistrationForm, AuthForm, TaskForm, EmployeeForm, TaskTagForm
from django.contrib.auth import get_user_model, authenticate, login, logout

User = get_user_model()

@login_required
def main_view(request):
    # order_by для того, чтобы сортировать (у нас по дате), а символ "-" - идёт в обратном порядке
    # TODO: Удалить или исправить
    #  timeslots = TimeSlot.objects.all().order_by('-start_date')
    employees = EmployeeAccount.objects.all()
    return render(request, 'web/main.html', {
        "employees": employees
        # "year" : year,
        # "timeslots": timeslots,
        # "form": TimeSlotForm(),
    })


def registration_view(request):
    form = RegistrationForm()
    is_success = False
    if request.method == "POST":
        form = RegistrationForm(data=request.POST)
        if form.is_valid():
            # если всё гуд, создаём модель пользователя
            user = User(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
            )
            user.set_password(form.cleaned_data['password'])
            user.save()
            is_success = True
            return redirect('auth')
    return render(request, 'web/registration.html',
                  {
                      "form": form,
                      "is_success": is_success
                  })


def auth_view(request):
    form = AuthForm()
    if request.method == "POST":
        form = AuthForm(data=request.POST)
        if form.is_valid():
            user = authenticate(**form.cleaned_data)  # если пользователь найден, то сюда запишется
            if user is None:
                form.add_error(None, "Введены неверные данные")
            else:
                # если пользователь обновит страницу, авторизация слетит, поэтому добавляем login
                login(request, user)
                # переброс на главную
                return redirect("main")
    return render(request, 'web/auth.html', {"form": form})


def logout_view(request):
    logout(request)
    return redirect("main")

@login_required
def project_view(request):
    # TODO: Реализовать
    return render(request, 'web/project.html', {})


@login_required
def profile_view(request):
    # TODO: Реализовать
    return render(request, 'web/profile.html', {})

@login_required
def employees_dashboard_view(request):
    # TODO: Реализовать
    return render(request, 'web/employees_dashboard.html', {})

@login_required
def projects_dashboard_view(request):
    # TODO: Реализовать
    return render(request, 'web/projects_dashboard.html', {})

@login_required
def calendar_view(request):
    # TODO: Реализовать
    return render(request, 'web/calendar.html', {})

@login_required
def feedback_view(request):
    # TODO: Реализовать
    return render(request, 'web/feedback.html', {})

@login_required
def add_task_view(request, id=None):
    form = TaskForm()
    if request.method == 'POST':
        form = TaskForm(data=request.POST, initial={"user": request.user})
        if form.is_valid():
            form.save()
            return redirect("main")
    return render(request, 'web/add_task.html', {"form": form})

@login_required
def add_employee_view(request):
    form = EmployeeForm()
    if request.method == 'POST':
        form = EmployeeForm(data=request.POST, files=request.FILES, initial={"user": request.user})
        if form.is_valid():
            form.save()
            return redirect("main")
    return render(request, 'web/add_employee.html', {"form": form})


@login_required
def task_tags_view(request):
    tags = TaskTag.objects.all() #Доступные теги
    form = TaskTagForm()
    if request.method == "POST":
        form = TaskTagForm(data=request.POST, initial={"user": request.user})
        if form.is_valid():
            form.save()
            return redirect('tags')
    return render(request, 'web/task_tags.html', {"tags": tags, "form": form})


def delete_task_tag_view(request, id):
    tag = get_object_or_404(TaskTag, user=request.user, id=id)
    tag.delete()
    return redirect('tags')

# TODO: Переделать формочки под models.py
# # @login_required # зачита от неавторизованности
# def time_slot_add_view(request):
#     if request.method == "POST":
#         form = TimeSlotForm(data=request.POST, files=request.FILES, initial={"user": request.user})
#         if form.is_valid():
#             form.save()
#             return redirect("main")
#     else:
#         form = TimeSlotForm(initial={"user": request.user})
#
#     return render(request, 'web/time_slot_form.html', {"form": form})
#
#
# def time_slot_edit_view(request, id=None):
#     timeslot = None
#     if id is not None:
#         timeslot = TimeSlot.objects.get(id=id)
#
#     if request.method == "POST":
#         form = TimeSlotForm(data=request.POST, files=request.FILES, instance=timeslot, initial={"user": request.user})
#         if form.is_valid():
#             form.save()
#             return redirect("main")  # перебрасываем в мейн
#     else:
#         form = TimeSlotForm(instance=timeslot, initial={"user": request.user})
#
#     return render(request, 'web/time_slot_form.html', {"form": form})
#
#
# def _list_editor_view(request, model_cls, form_cls, template_name, url_name):
#     items = model_cls.objects.all()
#     form = form_cls()
#     if request.method == "POST":
#         form = form_cls(data=request.POST, initial={"user": request.user})
#         if form.is_valid():
#             form.save()
#             return redirect(url_name)
#     return render(request, f'web/{template_name}.html', {"items": items, "form": form})
#
#
# def tags_view(request):
#     return _list_editor_view(request, TimeSlotTag, TimeSlotTagForm, "tags", "tags")
#
#
# def tags_delete_view(request, id):
#     tag = TimeSlotTag.objects.get(id=id)
#     tag.delete()
#     return redirect("tags")
#
#
# def holidays_view(request):
#     return _list_editor_view(request, Holiday, HolidayForm, "holidays", "holidays")
#
#
# def holidays_delete_view(request, id):
#     holiday = Holiday.objects.get(id=id)
#     holiday.delete()
#     return redirect("holidays")
