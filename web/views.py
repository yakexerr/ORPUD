from datetime import datetime

#--------- для отправки письма ------------


from django.core.mail import EmailMessage
from django.shortcuts import render, redirect
from .forms import FeedbackForm


#-------------------------------------------

from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect
from web.forms import RegistrationForm, AuthForm
from django.contrib.auth import get_user_model, authenticate, login
from .forms import FeedbackForm
User = get_user_model()

def main_view(request):
    year = datetime.now().year
    return render(request, 'web/main.html', {
        "year" : year,
    })
from datetime import datetime

from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.template.context_processors import request

from web.forms import RegistrationForm, AuthForm#, TimeSlotForm, TimeSlotTagForm, HolidayForm
from django.contrib.auth import get_user_model, authenticate, login, logout

# from web.models import TimeSlot, TimeSlotTag, Holiday

User = get_user_model()

@login_required
def main_view(request):
    # order_by для того, чтобы сортировать (у нас по дате), а символ "-" - идёт в обратном порядке
    # TODO: Удалить или исправить
    #  timeslots = TimeSlot.objects.all().order_by('-start_date')
    return render(request, 'web/main.html', {
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
    return render(request, 'web/registration.html',
    {
            "form": form,
            "is_success": is_success
            })
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

def auth_view(request):
    form = AuthForm()
    if request.method == "POST":
        form = AuthForm(data=request.POST)
        if form.is_valid():
            user = authenticate(**form.cleaned_data) # если пользователь найден, то сюда запишется
            if user is None:
                form.add_error(None, "Введены неверные данные")
            else:
                # если пользователь обновит страницу, авторизация слетит, поэтому добавляем login
                login(request, user)
                #переброс на главную
                return redirect("main")

    return render(request, 'web/auth.html', {"form": form})