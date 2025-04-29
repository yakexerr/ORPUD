from datetime import datetime
from django.urls import reverse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.template.context_processors import request
from django.views.generic import RedirectView

from web.models import *
from web.forms import *
from django.contrib.auth import get_user_model, authenticate, login, logout

#--------- для отправки письма ------------


from django.core.mail import EmailMessage
from django.shortcuts import render, redirect
from .forms import FeedbackForm


#-------------------------------------------
from django.shortcuts import render, get_object_or_404


User = get_user_model()

# Главная страница
@login_required
def main_view(request):
    user = request.user
    context = {}

    # Проверяем, является ли пользователь менеджером
    if user.role == 'manager':
        context['manager_account'] = user
        context['manager_projects'] = Project.objects.filter(manager=user)
        context['manager_employees'] = CustomUser.objects.filter(role='employee', id__in=context['manager_projects'].values_list('employees', flat=True)).distinct()

    # Если пользователь - сотрудник
    elif user.role == 'employee':
        context['employee_account'] = user
        context['employee_tasks'] = Task.objects.filter(employees=user)
        context['employee_projects'] = Project.objects.filter(employees=user)

    return render(request, 'web/main.html', context)


# Регистрация
def registration_view(request):
    form = RegistrationForm()
    is_success = False
    if request.method == "POST":
        form = RegistrationForm(data=request.POST)
        if form.is_valid():
            user = form.save()
            is_success = True
            return redirect('auth')
    return render(request, 'web/registration.html', {
        "form": form,
        "is_success": is_success,
    })

# Авторизация
def auth_view(request):
    form = AuthForm()
    if request.method == "POST":
        form = AuthForm(request.POST)
        if form.is_valid():
            user = authenticate(request, **form.cleaned_data)
            if user is None:
                form.add_error(None, "Введены неверные данные")
            else:
                # если пользователь обновит страницу, авторизация слетит, поэтому добавляем login
                login(request, user)
                # переброс на главную
                return redirect("main")
    return render(request, 'web/auth.html', {"form": form})


# Выход из системы
def logout_view(request):
    logout(request)
    return redirect("main")


#техническое сообщение по типу "Вы зарегистрированы"
def action_message_view(request):
    return render(request, 'web/action_message.html')


@login_required
def project_view(request, id=None):
    project = get_object_or_404(Project, id=id) if id is not None else None
    return render(request, 'web/project.html', {"project": project})


class first_project_redirect_view(RedirectView):
    permanent = False
    query_string = True

    def get_redirect_url(self, *args, **kwargs):
        employee = self.request.user
        if employee.role == 'manager':
            first_project = Project.objects.filter(manager=employee).order_by('-date_create').first()
        if employee.role == 'employee':
            first_project = Project.objects.filter(employees=employee).order_by('-date_create').first()
        if first_project:
            return f"/project/{first_project.id}/"
        return "/project/empty"

@login_required
def edit_project_view(request, id=None):
    project = get_object_or_404(Project, id=id) if id is not None else None
    form = ProjectForm(instance=project)
    if request.method == 'POST':
        form = ProjectForm(data=request.POST, instance=project, files=request.FILES)
        if form.is_valid():
            form.save()
            return redirect(reverse('current_project', args=[id]))
    return render(request, 'web/edit_project.html', {"form": form})


@login_required
def profile_view(request, id=None):
    employee = get_object_or_404(User, id=id) if id is not None else request.user
    if employee.role == 'manager':
        projects = Project.objects.filter(manager=employee)
    if employee.role == 'employee':
        projects = Project.objects.filter(employees=employee)
    return render(request, 'web/profile.html', {"employee": employee, "projects": projects})

@login_required
def edit_profile_view(request):
    profile = request.user
    form = EmployeeForm(instance=profile)
    if request.method == 'POST':
        form = EmployeeForm(data=request.POST, instance=profile, files=request.FILES)
        if form.is_valid():
            form.save()
            return redirect("my_profile")
    return render(request, 'web/edit_employee.html', {"form": form})


@login_required
def delete_profile_view(request):
    employee = get_object_or_404(User, id=request.user.id)
    employee.delete()
    return render(
        request,
        'web/action_message.html',
        {"action_message": "delete_profile"}
    )

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
    if request.method == "POST":
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save()

            subject = "Новое сообщение с формы обратной связи"
            message = f"""
                Имя: {feedback.name}
                Фамилия: {feedback.last_name}
                Email: {feedback.email}
                Телефон: {feedback.phone}
                Сообщение:
                {feedback.message}
            """
            email = EmailMessage(
                subject,
                message,
                'task_trackerorpud@mail.ru',  # От кого
                ['task_trackerorpud@mail.ru'],  # Кому
            )
            email.reply_to = [feedback.email]  # Почта пользователя для ответа
            email.send(fail_silently=False)
            return redirect("feedback")
    else:
        form = FeedbackForm()
    return render(request, 'web/feedback.html', {"form": form})

# Добавление задачи
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


# Добавление сотрудника
@login_required
def edit_employee_view(request, id=None):
    employee = get_object_or_404(User, id=id) if id is not None else None
    form = EmployeeForm(instance=employee)
    if request.method == 'POST':

        email = request.POST.get('email', '')
        fio = request.POST.get('fio', '')

        email_prefix = email.split('@')[0]
        fio_initials = ''.join([el[0] for el in fio.strip().split()])
        auto_username = f"{email_prefix}{fio_initials}"

        form = EmployeeForm(data=request.POST, instance=employee, files=request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = auto_username
            user.save()
            return redirect("employees")
    return render(request, 'web/add_employee.html', {"form": form})


@login_required
def employees_view(request):
    employees = CustomUser.objects.filter(role='employee')
    return render(request, 'web/employees.html', {"employees": employees})

@login_required
def delete_employee_view(request, id):
    task = get_object_or_404(User, id=id)
    task.delete()
    return redirect('employees')


# Управление тегами задач
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


# Удаление тега задачи
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
def current_task_view(request, id=None):
    task = get_object_or_404(Task, id=id) if id is not None else None
    return render(request, 'web/task.html', {"task": task})


@login_required
def completed_task_view(request):
    tasks = Task.objects.all().filter(user=request.user, is_done=True).order_by('-priority')
    return render(request, 'web/completed_task_test.html', {"tasks": tasks})


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