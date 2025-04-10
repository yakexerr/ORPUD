from datetime import datetime

from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect
from django.template.context_processors import request

from web.forms import RegistrationForm, AuthForm, TimeSlotForm
from django.contrib.auth import get_user_model, authenticate, login, logout

from web.models import TimeSlot

User = get_user_model()

def main_view(request):
    # year = datetime.now().year
    timeslots = TimeSlot.objects.all()
    return render(request, 'web/main.html', {
        # "year" : year,
        "timeslots" : timeslots,
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
            user = authenticate(**form.cleaned_data) # если пользователь найден, то сюда запишется
            if user is None:
                form.add_error(None, "Введены неверные данные")
            else:
                # если пользователь обновит страницу, авторизация слетит, поэтому добавляем login
                login(request, user)
                #переброс на главную
                return redirect("main")
    return render(request, 'web/auth.html', {"form": form})

def logout_view(request):
    logout(request)
    return redirect("main")

# @login_required # зачита от неавторизованности
def time_slot_add_view(request):
    if request.method == "POST":
        form = TimeSlotForm(data=request.POST, files=request.FILES, initial={"user": request.user})
        if form.is_valid():
            form.save()
            return redirect("main")
    else:
        form = TimeSlotForm(initial={"user": request.user})

    return render(request, 'web/time_slot_form.html', {"form": form})


def time_slot_edit_view(request, id=None):
    timeslot = None
    if id is not None:
        timeslot = TimeSlot.objects.get(id=id)

    if request.method == "POST":
        form = TimeSlotForm(data=request.POST, files=request.FILES, instance=timeslot, initial={"user": request.user})
        if form.is_valid():
            form.save()
            return redirect("main")
    else:
        form = TimeSlotForm(instance=timeslot, initial={"user": request.user})

    return render(request, 'web/time_slot_form.html', {"form": form})
