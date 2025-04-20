from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.template.context_processors import request
from web.models import Task, EmployeeAccount, TaskTag, Project, EmployeeAccount, Task, ManagerAccount
from web.forms import RegistrationForm, AuthForm, TaskForm, EmployeeForm, TaskTagForm
from django.contrib.auth import get_user_model, authenticate, login, logout

User = get_user_model()

@login_required
def main_view(request):
    user = request.user
    context = {}

    try:
        manager = ManagerAccount.objects.get(email=user.email)
        context['manager_account'] = manager
        context['manager_projects'] = Project.objects.filter(manager=manager)
        context['manager_employees'] = EmployeeAccount.objects.filter(
            id__in=context['manager_projects'].values_list('employees', flat=True)
        ).distinct()
    except ManagerAccount.DoesNotExist:
        pass

    try:
        employee = EmployeeAccount.objects.get(email=user.email)
        context['employee_account'] = employee
        context['employee_tasks'] = Task.objects.filter(employees=employee)
        context['employee_projects'] = Project.objects.filter(employees=employee)
    except EmployeeAccount.DoesNotExist:
        pass

    return render(request, 'web/main.html', context)



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
    employee = request.user
    # employee = get_object_or_404(EmployeeAccount, user=request.user, id=id) if id is not None else None
    return render(request, 'web/profile.html', {"employee": employee})

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
def edit_task_view(request, id=None):
    task = get_object_or_404(Task, user=request.user, id=id) if id is not None else None
    form = TaskForm(instance=task)
    if request.method == 'POST':
        form = TaskForm(data=request.POST, instance=task, initial={"user": request.user})
        if form.is_valid():
            form.save()
            return redirect("main")
    return render(request, 'web/add_task.html', {"form": form})


@login_required
def delete_task_view(request, id):
    task = get_object_or_404(Task, user=request.user, id=id)
    task.delete()
    return redirect('tasks')


@login_required
def complete_task_view(request, id):
    task = get_object_or_404(Task, user=request.user, id=id)
    if not task.is_done:
        task.is_done = True
    else:
        task.is_done = False
    task.save()
    return redirect('tasks')


@login_required
def task_view(request): #для теста редактирования\удаления задач
    tasks = Task.objects.all().filter(user=request.user, is_done=False).order_by('-priority')
    return render(request, 'web/task_test.html', {"tasks": tasks})


@login_required
def completed_task_view(request):
    tasks = Task.objects.all().filter(user=request.user, is_done=True).order_by('-priority')
    return render(request, 'web/completed_task_test.html', {"tasks": tasks})

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

@login_required
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
