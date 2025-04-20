from django import forms
from django.contrib.auth import get_user_model
from web.models import Task, EmployeeAccount, TaskTag, ManagerAccount

User = get_user_model()


class RegistrationForm(forms.ModelForm):
    password2 = forms.CharField(widget=forms.PasswordInput) #чтобы пароль не отображался

    def clean(self):
        # доп валидацию можно сделать сдесь или с валидаторами, которые привязваются к полю
        cleaned_data = super().clean()
        if cleaned_data['password'] != cleaned_data['password2']:
            self.add_error('password', 'Пароли не совпадают')
        return cleaned_data

    class Meta:
        model = User
        fields = ('email', 'username', 'password', 'password2')


class AuthForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)


class TaskForm(forms.ModelForm):
    deadline = forms.DateTimeField(widget=forms.DateTimeInput(attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%m"), label="Дедлайн")
    forms.ChoiceField(choices=Task.PRIORITY_CHOICES, widget=forms.Select, initial=Task.MEDIUM, label="Приоритет")

    #Чтобы выбрать несколько тегов, зажми Ctrl+Shift (Это для страницы в браузере)

    def save(self, commit=True):
        self.instance.user = self.initial['user']
        return super().save(commit)

    class Meta:
        model = Task
        exclude = ('user', 'is_done', 'date_added')


class TaskTagForm(forms.ModelForm):
    def save(self, commit=True):
        self.instance.user = self.initial['user']
        return super().save(commit)

    class Meta:
        model = TaskTag
        fields = ("title", )

class EmployeeForm(forms.ModelForm):
    class Meta:
        model = EmployeeAccount
        fields = ('fio', 'position', 'email', 'phone', 'image', )

class ManagerForm(forms.ModelForm):
    class Meta:
        model = ManagerAccount
        fields = ('fio', 'position', 'email', 'image', )

# TODO: переделать в соответствии с models.py
'''
class TimeSlotForm(forms.ModelForm):
    # переопределяем метод save
    def save(self, commit=True):
        self.instance.user = self.initial['user']
        return super().save(commit)

    class Meta:
        model = TimeSlot # указываем что форма на модели таймслот
        fields = ('title', 'start_date', 'end_date', 'image', 'tags')
        widgets = {
            "start_date": forms.DateTimeInput(
                attrs={"type": "datetime-local"}, format='%Y-%m-%dT%H:%M'
            ),
            "end_date": forms.DateTimeInput(
                attrs={"type": "datetime-local"}, format='%Y-%m-%dT%H:%M'
            )
        }

class TimeSlotTagForm(forms.ModelForm):
    # переопределяем метод save
    def save(self, commit=True):
        self.instance.user = self.initial['user']
        return super().save(commit)

    class Meta:
        model = TimeSlotTag # указываем что форма на модели таймслот
        fields = ('title',)


class HolidayForm(forms.ModelForm):
    # переопределяем метод save
    def save(self, commit=True):
        self.instance.user = self.initial['user']
        return super().save(commit)

    class Meta:
        model = Holiday # указываем что форма на модели таймслот
        fields = ('date',)
        widgets = {
            "date": forms.DateTimeInput(
                attrs={"type": "date"}, format='%Y-%m-%d'
            ),
        }
'''