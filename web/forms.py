from django import forms
from django.contrib.auth import get_user_model
from web.models import FeedBack

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


class FeedbackForm(forms.ModelForm):
    class Meta:
        model = FeedBack
        fields = ['name', 'last_name', 'email', 'phone', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Введите Ваше имя'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Введите Вашу фамилию'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Введите Ваш email'}),
            'phone': forms.TextInput(attrs={'placeholder': 'Введите Ваш телефон'}),
            'message': forms.Textarea(attrs={'placeholder': 'Введите Ваше сообщение', 'rows': 4}),
        }
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


class ProjectForm(forms.ModelForm):
    deadline = forms.DateTimeField(widget=forms.DateTimeInput(attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%m"), label="Дедлайн")
    class Meta:
        model = Project
        fields = ('title', 'description', 'deadline', 'tasks', 'employees')

class TaskFilterForm(forms.Form):
    tag = forms.ChoiceField(
        choices=[('', 'Тег')],
        widget=forms.Select,
        required=False
    )
    search = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': "Поиск по слову"}),
        required=False
    )
    priority = forms.ChoiceField(
        choices=[('', 'Приоритет')] + Task.PRIORITY_CHOICES,
        widget=forms.Select,
        required=False
    )
    employee = forms.ChoiceField(
        choices=[],
        widget=forms.Select,
        required=False
    )
    deadline = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%m"),
        required=False,
        label="Дедлайн"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Наполняем choices только если таблицы уже существуют
        try:
            self.fields['tag'].choices += [
                (tag.id, str(tag)) for tag in TaskTag.objects.all()
            ]
            self.fields['employee'].choices = [('', 'Сотрудник')] + [
                (user.id, str(user)) for user in User.objects.filter(role='employee')
            ]
        except Exception as e:
            # Можно логировать или просто игнорировать при запуске миграций
            pass



class ProjectFilterForm(forms.Form):
    search = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': "Поиск по слову"}),
        required=False
    )
    is_done = forms.NullBooleanField(
        widget=forms.Select(choices=[
            (None, 'Статус'),
            (True, 'Выполнен'),
            (False, 'Не выполнен')
        ]),
        required=False
    )
    task = forms.ChoiceField(
        choices=[('', 'Задача')],
        widget=forms.Select,
        required=False
    )
    deadline = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%m"),
        required=False,
        label="Дедлайн"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            self.fields['task'].choices += [(task.id, str(task)) for task in Task.objects.all()]
        except Exception:
            pass  # игнорируем ошибку, если таблица Task не создана (например, при миграции)
