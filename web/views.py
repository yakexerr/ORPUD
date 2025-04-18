from datetime import datetime

from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect, get_object_or_404
from django.template.context_processors import request
from django.utils.timezone import now
from web.forms import RegistrationForm, AuthForm, TimeSlotForm, TimeSlotTagForm, HolidayForm
from django.contrib.auth import get_user_model, authenticate, login, logout
from django.contrib.auth.decorators import login_required
from web.models import TimeSlot, TimeSlotTag, Holiday

from  django.core.paginator import Paginator


User = get_user_model()

@login_required # а тут чтоб не было видно задач у неавториз. юзера
def main_view(request):
    # order_by для того, чтобы сортировать (у нас по дате), а символ "-" - идёт в обратном порядке
    timeslots = TimeSlot.objects.filter(user=request.user).order_by('-start_date') # filter(user=request.user) - пользователь таймслота должен быть равен нынешнему пользователю ,тогда другие не смогут видеть чужие таймслоты
    print("QUERY", timeslots.query) # конкретный запрос можно вывести так
    # делаем так, чтоб вместо добавления вверху текущий таймслот выводился
    current_timeslot = timeslots.filter(end_date__isnull=True).first()

    # делаем пагинатор, чтобы данные выводились по страничкам, а не 1 списком
    page_number = request.GET.get('page',1) # юерём запроси и если там нет опред. страницы, то возвращаем 1ю
    paginator = Paginator(timeslots, per_page=10)
    return render(request, 'web/main.html', {
        "current_timeslot": current_timeslot,
        "timeslots": paginator.get_page(page_number),
        "form": TimeSlotForm(),
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


def logout_view(request):
    logout(request)
    return redirect("main")


@login_required # защита от неавторизованности
def time_slot_add_view(request):
    if request.method == "POST":
        form = TimeSlotForm(data=request.POST, files=request.FILES, initial={"user": request.user})
        if form.is_valid():
            form.save()
            return redirect("main")
    else:
        form = TimeSlotForm(initial={"user": request.user})

    return render(request, 'web/time_slot_form.html', {"form": form})

@login_required
def time_slot_edit_view(request, id=None):
    timeslot = None
    if id is not None:
        timeslot = get_object_or_404(TimeSlot, user=request.user,id=id)

    if request.method == "POST":
        form = TimeSlotForm(data=request.POST, files=request.FILES, instance=timeslot, initial={"user": request.user})
        if form.is_valid():
            form.save()
            return redirect("main")  # перебрасываем в мейн
    else:
        form = TimeSlotForm(instance=timeslot, initial={"user": request.user})

    return render(request, 'web/time_slot_form.html', {"form": form})

@login_required
def time_slot_stop_view(request, id):
    if request.method == "POST":
        timeslot = get_object_or_404(TimeSlot, user=request.user,id=id) # помогает запрашивать из базы данных тем же условием, но если не будет объекта, то выведет 404 страницу
        timeslot.end_date = now()
        timeslot.save()
    return redirect("main")

@login_required
def time_slot_delete_view(request, id):
    tag = get_object_or_404(TimeSlot, user=request.user,id=id)
    tag.delete()
    return redirect("main")


def _list_editor_view(request, model_cls, form_cls, template_name, url_name):
    items = model_cls.objects.filter(user=request.user)
    form = form_cls()
    if request.method == "POST":
        form = form_cls(data=request.POST, initial={"user": request.user})
        if form.is_valid():
            form.save()
            return redirect(url_name)
    return render(request, f'web/{template_name}.html', {"items": items, "form": form})

@login_required
def tags_view(request):
    return _list_editor_view(request, TimeSlotTag, TimeSlotTagForm, "tags", "tags")

@login_required
def tags_delete_view(request, id):
    tag = get_object_or_404(TimeSlotTag, user=request.user, id=id)
    tag.delete()
    return redirect("tags")

@login_required
def holidays_view(request):
    return _list_editor_view(request, Holiday, HolidayForm, "holidays", "holidays")

@login_required
def holidays_delete_view(request, id):
    holiday = get_object_or_404(Holiday, user=request.user, id=id)
    holiday.delete()
    return redirect("holidays")
