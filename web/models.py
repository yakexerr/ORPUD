from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()


class ManagerAccount(models.Model):
    fio = models.CharField(max_length=256, verbose_name="ФИО", null=False, blank=False)
    image = models.ImageField(upload_to='img/account_avatars/', null=True, blank=True, verbose_name="Фото")
    position = models.CharField(max_length=256, verbose_name="Должность")
    email = models.EmailField(max_length=256, verbose_name="Email")

    def __str__(self):
        return self.fio


class EmployeeAccount(models.Model):
    fio = models.CharField(max_length=256, verbose_name="ФИО", null=False, blank=False)
    image = models.ImageField(upload_to='img/account_avatars/', null=True, blank=True, verbose_name="Фото")
    position = models.CharField(max_length=256, verbose_name="Должность")
    email = models.EmailField(max_length=256, verbose_name="Email")
    phone = models.CharField(max_length=256, verbose_name="Телефон")

    def __str__(self):
        return self.fio


class TaskTag(models.Model):
    title = models.CharField(max_length=256, verbose_name="Название", null=False, blank=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class Task(models.Model):
    HIGH = 3
    MEDIUM = 2
    LOW = 1

    PRIORITY_CHOICES = [
        (HIGH, "High"),
        (MEDIUM, "Medium"),
        (LOW, "Low")
    ]

    title = models.CharField(max_length=256, verbose_name="Название", default='Без названия')
    description = models.TextField(max_length=512, default="", verbose_name="Описание")
    priority = models.IntegerField(choices=PRIORITY_CHOICES, default=MEDIUM)
    date_added = models.DateTimeField(default=timezone.now)
    deadline = models.DateTimeField()
    tags = models.ManyToManyField(TaskTag, verbose_name="Теги", blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    employees = models.ManyToManyField(EmployeeAccount, verbose_name="Работники")
    is_done = models.BooleanField(default=False)


class TaskLogs(models.Model): #Если что переименуйте
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    date_task_take = models.DateTimeField()
    date_task_close = models.DateTimeField()


class TaskComment:
    date_sent = models.DateTimeField()
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    comment_text = models.CharField(max_length=256, null=False, blank=False, verbose_name="Название")


class Project(models.Model):
    title = models.CharField(max_length=256, verbose_name="Название", default='Без названия')
    description = models.CharField(max_length=512, default="", verbose_name="Описание")
    date_create = models.DateTimeField(default=timezone.now)
    deadline = models.DateTimeField()
    is_done = models.BooleanField(default=False)
    tasks = models.ManyToManyField(Task, verbose_name="Задачи")
    manager = models.ForeignKey(ManagerAccount, default=1, verbose_name="Менеджер", on_delete=models.PROTECT)
    employees = models.ManyToManyField(EmployeeAccount, verbose_name="Работники")

    def __str__(self):
        return f"{self.title}, owner: {self.manager}"
