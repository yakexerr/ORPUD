from django import forms
from django.contrib.auth import get_user_model
from web.models import *

User = get_user_model()

class RegistrationForm(forms.ModelForm):
    password2 = forms.CharField(widget=forms.PasswordInput, label="Повторите пароль")
    password = forms.CharField(widget=forms.PasswordInput, label="Пароль")
    fio = forms.CharField(max_length=256, label="ФИО")  # Добавлено поле fio

    ROLE_CHOICES = [
        ('manager', 'Менеджер'),
        ('employee', 'Сотрудник')
    ]

    role = forms.ChoiceField(choices=ROLE_CHOICES, label="Роль")

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('password') != cleaned_data.get('password2'):
            self.add_error('password2', 'Пароли не совпадают')
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password2', 'role', 'fio')


class AuthForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)


class TaskForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['employees'].queryset = User.objects.filter(role='employee')

    deadline = forms.DateTimeField(widget=forms.DateTimeInput(attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%m"), label="Дедлайн")
    priority = forms.ChoiceField(
        choices=Task.PRIORITY_CHOICES,
        widget=forms.Select,
        initial=Task.MEDIUM,
        label="Приоритет"
    )

    #Чтобы выбрать несколько тегов, зажми Ctrl+Shift (Это для страницы в браузере)

    def save(self, commit=True):
        user = self.initial.get('user')
        if user:
            self.instance.user = user
        return super().save(commit)

    class Meta:
        model = Task
        exclude = ('user', 'is_done', 'date_added')


class TaskTagForm(forms.ModelForm):
    def save(self, commit=True):
        user = self.initial.get('user')
        if user:
            self.instance.user = user
        return super().save(commit)

    class Meta:
        model = TaskTag
        fields = ("title", )

class EmployeeForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('fio', 'position', 'email', 'phone', 'image')