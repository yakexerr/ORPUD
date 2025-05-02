from datetime import datetime
from web.services import task_filter, project_filter
from django.core.paginator import Paginator
from django.urls import reverse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.template.context_processors import request
from django.views import View
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
from django.utils.timezone import now
from datetime import timedelta
import json
import random

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


class first_project_redirect_view(View):
    permanent = False
    query_string = True

    def get(self, request, *args, **kwargs):
        employee = self.request.user
        if employee.role == 'manager':
            first_project = Project.objects.filter(manager=employee).order_by('-date_create').first()
        if employee.role == 'employee':
            first_project = Project.objects.filter(employees=employee).order_by('-date_create').first()
        if first_project:
            return redirect('current_project', first_project.id)
        return render(request, 'web/project.html', {"project": None})

@login_required
def edit_project_view(request, id=None):
    project = get_object_or_404(Project, id=id) if id is not None else None
    form = ProjectForm(instance=project)
    if request.method == 'POST':
        form = ProjectForm(data=request.POST, instance=project, files=request.FILES)
        if form.is_valid():
            form.save()
            return redirect('projects')
    return render(request, 'web/edit_project.html', {"form": form})


@login_required
def complete_project_view(request, id):
    project = get_object_or_404(Project, id=id)
    if not project.is_done:
        project.is_done = True
    else:
        project.is_done = False
    project.save()
    return redirect('main')

@login_required
def projects_view(request):
    if request.user.role == 'manager':
        projects = Project.objects.all().filter(manager=request.user)

        filter_form = ProjectFilterForm(request.GET)
        filter_form.is_valid()
        projects = project_filter(projects, filter_form.cleaned_data)

        total_count = projects.count()
        page = request.GET.get("page", 1)
        paginator = Paginator(projects, per_page=10)

        return render(request, 'web/all_projects.html', {
            "projects": paginator.get_page(page),
            "filter_form": filter_form,
            "total_count": total_count
        })
    if request.user.role == 'employee':
        project = Project.objects.all().filter(employees=request.user).first()
        return redirect(reverse('current_project', args=[project.id]))
    return redirect('main')


@login_required
def delete_project_view(request, id):
    project = get_object_or_404(Project, id=id)
    project.delete()
    return redirect('projects')

@login_required
def profile_view(request, id=None):
    employee = get_object_or_404(User, id=id) if id is not None else request.user
    if employee.role == 'manager':
        projects = Project.objects.filter(manager=employee)
    if employee.role == 'employee':
        projects = Project.objects.filter(employees=employee)
        tasks = Task.objects.filter(employees=employee)
        return render(request, 'web/profile.html', {"employee": employee, "projects": projects, "tasks": tasks})
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

    # Статистика по выполненным и невыполненным задачам
    completed_tasks = Task.objects.filter(is_done=True, user=request.user)
    not_completed_tasks = Task.objects.filter(is_done=False, user=request.user)

    # Считаем задачи по приоритетам
    completed_priority = {
        'High': completed_tasks.filter(priority=Task.HIGH).count(),
        'Medium': completed_tasks.filter(priority=Task.MEDIUM).count(),
        'Low': completed_tasks.filter(priority=Task.LOW).count(),
    }

    not_completed_priority = {
        'High': not_completed_tasks.filter(priority=Task.HIGH).count(),
        'Medium': not_completed_tasks.filter(priority=Task.MEDIUM).count(),
        'Low': not_completed_tasks.filter(priority=Task.LOW).count(),
    }

    context = {
        'completed_priority': completed_priority,
        'not_completed_priority': not_completed_priority,
    }
    return render(request, 'web/projects_dashboard.html', context)

# Календарный график
def get_project_color(project_id):
    colors = ['#6f42c1', '#007bff', '#20c997', '#ffc107', '#fd7e14', '#e83e8c']
    return colors[project_id % len(colors)] + '33'  # '33' — это ~20% прозрачности

def get_task_color(priority):
    if priority == Task.HIGH:
        return '#e74c3c33'  # Красный
    elif priority == Task.MEDIUM:
        return '#f1c40f33'  # Жёлтый
    elif priority == Task.LOW:
        return '#2ecc7133'  # Зелёный
    return '#3498db33'     # Синий по умолчанию

@login_required
def calendar_view(request):
    projects = Project.objects.prefetch_related('tasks')
    data = []
    groups = []

    if projects.exists():
        for project in projects:
            color = get_project_color(project.id)
            groups.append({
                'id': project.id,
                'content': f"<div><strong>{project.title}</strong><br><small>Дедлайн: {project.deadline.strftime('%d.%m.%Y')}</small></div>",
                'style': f"background-color: {color}; color: darkslategray; font-weight: bold; padding: 4px; border-radius: 4px;"
            })
            for task in project.tasks.all():
                start = task.date_added
                end = task.deadline
                if end <= start:
                    end = start + timedelta(days=1)

                data.append({
                    'id': task.id,
                    'group': project.id,
                    'content': task.title,
                    'start': start.isoformat(),
                    'end': end.isoformat(),
                    'title': f'Задача: {task.title}\nОтветственный: {task.user.fio}\nПриоритет: {task.get_priority_display()}',
                    'style': f'background-color: {get_task_color(task.priority)};'
                })
    else:
        # Добавим заглушку-группу и задачу, чтобы диаграмма всё равно отобразилась
        groups.append({'id': 0, 'content': 'Нет проектов', 'style': 'background-color: #ccc;'})
        data.append({
            'id': 0,
            'group': 0,
            'content': 'Нет задач',
            'start': timezone.now().isoformat(),
            'end': (timezone.now() + timedelta(days=1)).isoformat(),
            'style': 'background-color: #aaa;'
        })

    context = {
        'tasks_json': json.dumps(data),
        'groups_json': json.dumps(groups),
    }
    return render(request, 'web/calendar.html', context)

@login_required
def feedback_view(request):
    if request.method == "POST":
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save()

            # Формируем письмо
            subject = "Новое сообщение с формы обратной связи"
            message = f"""
                Имя: {feedback.name}
                Фамилия: {feedback.last_name}
                Email: {feedback.email}
                Телефон: {feedback.phone}
                Сообщение:
                {feedback.message}
            """
            # Создаём объект EmailMessage
            email = EmailMessage(
                subject,
                message,
                'task_trackerorpud@mail.ru',  # От кого
                ['task_trackerorpud@mail.ru'],  # Кому
            )
            # Добавляем заголовок Reply-To
            email.reply_to = [feedback.email]  # Почта пользователя для ответа
            # Отправляем письмо
            email.send(fail_silently=False)
            return redirect("feedback")
    else:
        form = FeedbackForm()
    return render(request, 'web/feedback.html', {"form": form})

# Добавление задачи
@login_required
def edit_task_view(request, id=None):
    task = get_object_or_404(Task, id=id) if id is not None else None
    form = TaskForm(instance=task)
    if request.method == 'POST':
        form = TaskForm(data=request.POST, instance=task, initial={"user": request.user})
        if form.is_valid():
            form.save()
            return redirect("tasks")
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
    task = get_object_or_404(Task, id=id)
    if not task.is_done:
        task.is_done = True
    else:
        task.is_done = False
    task.save()
    return redirect('tasks')


@login_required
def task_view(request): #для теста редактирования\удаления задач
    if request.user.role == 'manager':
        tasks = Task.objects.all().filter(is_done=False).order_by('-priority')
    if request.user.role == 'employee':
        tasks = Task.objects.all().filter(is_done=False, employees=request.user).order_by('-priority')

    filter_form = TaskFilterForm(request.GET)
    filter_form.is_valid()
    tasks = task_filter(tasks, filter_form.cleaned_data)

    total_count = tasks.count()
    page = request.GET.get("page", 1)
    paginator = Paginator(tasks, per_page=10)

    return render(request, 'web/task_test.html', {
        "tasks": paginator.get_page(page),
        "filter_form": filter_form,
        "total_count": total_count
    })

@login_required
def current_task_view(request, id=None):
    task = get_object_or_404(Task, id=id) if id is not None else None
    return render(request, 'web/task.html', {"task": task})


@login_required
def completed_task_view(request):
    if request.user.role == 'manager':
        tasks = Task.objects.all().filter(employees__in=request.user.managed_projects.values('employees'), is_done=True).order_by('-priority').distinct()
    if request.user.role == 'employee':
        tasks = Task.objects.all().filter(employees=request.user, is_done=True).order_by('-priority')

    total_count = tasks.count()
    page = request.GET.get("page", 1)
    paginator = Paginator(tasks, per_page=10)

    return render(request, 'web/completed_task_test.html', {
        "tasks": paginator.get_page(page),
        "total_count": total_count
    })


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