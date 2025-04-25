from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.template.context_processors import request
from web.models import *
from web.forms import *
from django.contrib.auth import get_user_model, authenticate, login, logout

#--------- для отправки письма ------------


from django.core.mail import EmailMessage
from django.shortcuts import render, redirect
from .forms import FeedbackForm


#-------------------------------------------
from django.shortcuts import render, get_object_or_404

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
        "is_success": is_success
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
            # Перенаправляем пользователя на главную страницу
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


# Create your views here.
@login_required
def add_employee_view(request):
    form = EmployeeForm()
    if request.method == 'POST':
        form = EmployeeForm(data=request.POST, files=request.FILES, initial={"user": request.user})
        if form.is_valid():
            form.save()
            return redirect("main")
    return render(request, 'web/add_employee.html', {"form": form})


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

def employees_view(request):
    employees = CustomUser.objects.filter(role='employee')
    return render(request, 'web/employees.html', {"employees": employees})



#-----------------------------




def task_list_view(request):
    """
    Список всех задач. Шаблон task_test.html
    """
    tasks = Task.objects.all().order_by('-date_added')
    return render(request, 'web/task_test.html', {
        'tasks': tasks
    })

def task_detail_view(request, task_id):
    """
    Поля одной задачи. Шаблон task_detail.html
    """
    task = get_object_or_404(Task, id=task_id)
    return render(request, 'web/task_detail.html', {
        'task': task
    })

def user_tasks_view(request):
    """
    Список задач, привязанных к текущему пользователю.
    """
    tasks = Task.objects.filter(user=request.user).order_by('-date_added')
    return render(request, 'web/task_test.html', {
        'tasks': tasks
    })

def project_tasks_view(request, project_id):
    """
    Если нужен просмотр по проекту, и у тебя в модели Project есть поле tasks = ManyToManyField(Task)
    """
    project = get_object_or_404(Project, id=project_id)
    tasks = project.tasks.all().order_by('-date_added')
    return render(request, 'web/task_test.html', {
        'tasks': tasks,
        'project': project
    })

# TODO: Переделать формочки под models.py
# # @login_required # зачита от неавторизованности пользователя
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
