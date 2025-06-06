from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.conf import settings

class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, fio, password=None, role='employee', **extra_fields):
        if not username:
            raise ValueError('Username обязателен')
        if not email:
            raise ValueError('Email обязателен')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, fio=fio, role=role, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, fio, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(username, email, fio, password, role='manager', **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('manager', 'Менеджер'),
        ('employee', 'Сотрудник'),
    ]

    username = models.CharField(unique=True, max_length=256, verbose_name='Username')  # Логин
    email = models.EmailField(unique=True, verbose_name='Email')
    fio = models.CharField(max_length=256, verbose_name="ФИО")
    image = models.ImageField(upload_to='img/account_avatars/', null=True, blank=True, verbose_name="Фото")
    position = models.CharField(max_length=256, blank=True, verbose_name="Должность")
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Телефон")

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='employee')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)  # Для админки

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'  # Используем username как логин
    REQUIRED_FIELDS = ['email', 'fio']

    def __str__(self):
        return f'{self.fio} ({self.get_role_display()})'

class TaskTag(models.Model):
    title = models.CharField(max_length=256, verbose_name="Название", null=False, blank=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

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
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="created_tasks")
    employees = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='TaskEmployee',
        related_name='assigned_tasks',
        verbose_name="Работники"
    )
    is_done = models.BooleanField(default=False)

    def __str__(self):
        return self.title

class TaskEmployee(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    employee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date_task_take = models.DateTimeField(null=True, blank=True)
    date_task_close = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('task', 'employee')

class Project(models.Model):
    title = models.CharField(max_length=256, verbose_name="Название", default='Без названия')
    description = models.CharField(max_length=512, default="", verbose_name="Описание")
    date_create = models.DateTimeField(default=timezone.now)
    deadline = models.DateTimeField()
    is_done = models.BooleanField(default=False)
    tasks = models.ManyToManyField(Task, verbose_name="Задачи")
    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        limit_choices_to={'role': 'manager'},  # только менеджеры
        verbose_name="Менеджер",
        on_delete=models.PROTECT,
        related_name="managed_projects",
    )
    employees = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="projects",
        limit_choices_to={'role': 'employee'},
        verbose_name="Работники"
    )

    def get_columns(self):
        columns = Column.objects.filter(columnproject__project=self)

        if not columns.exists():
            # Создаём или получаем колонку "Не распределено"
            default_column, _ = Column.objects.get_or_create(name="Не распределено")
            ColumnProject.objects.get_or_create(project=self, column=default_column)

            # Привязываем все задачи проекта к этой колонке, если у них нет привязки
            for task in self.tasks.all():
                ColumnTask.objects.get_or_create(task=task, defaults={"column": default_column})

            # Повторно загружаем колонки
            columns = Column.objects.filter(columnproject__project=self)

        return columns

    def get_tasks_by_column(self, column):
        return self.tasks.filter(columntask__column=column)

    def __str__(self):
        return f"{self.title}, owner: {self.manager}"


class FeedBack(models.Model):
    name = models.CharField('Имя', max_length=100)
    last_name = models.CharField('Фамилия', max_length=100, blank=True, null=True)
    email = models.EmailField('Почта')
    phone = models.CharField('Телефон:', max_length=20, blank=True)
    message = models.TextField('Сообщение')
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)

    def __str__(self):
        return self.name

class Column(models.Model):
    name = models.CharField(max_length=100)

class ColumnProject(models.Model):
    column = models.ForeignKey(Column, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)

class ColumnTask(models.Model):
    column = models.ForeignKey(Column, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)