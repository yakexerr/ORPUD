import uuid
import random
from datetime import timedelta
from faker import Faker

from django.core.management.base import BaseCommand
from django.db import connection
from django.utils import timezone

from web.models import (
    CustomUser, TaskTag, Task, TaskEmployee,
    Project, FeedBack, Column, ColumnProject, ColumnTask
)

fake = Faker('ru_RU')


# SQL Profiler
def print_queries(queries):
    tag = uuid.uuid4()
    print(f"[{tag}] SQL PROFILER")
    total_time = 0.0
    total_queries = 0
    for counter, query in enumerate(queries, start=1):
        nice_sql = query["sql"].replace('"', "").replace(",", ", ")
        sql = "\033[1;31m[%s]\033[0m %s" % (query["time"], nice_sql)
        total_time += float(query["time"])
        print(f"[{tag}] {sql}\n")
        total_queries = counter
    print(f"[{tag}] \033[1;32m[" f"TOTAL TIME: {total_time} seconds, QUERIES: {total_queries}" f"]\033[0m")


# Constants
NUM_MANAGERS = 3
NUM_EMPLOYEES = 10
NUM_TAGS = 20
NUM_TASKS = 30
NUM_PROJECTS = 5
NUM_FEEDBACKS = 10


class Command(BaseCommand):
    help = "Генерирует тестовые данные для моделей: пользователей, задач, проектов и прочего"

    def handle(self, *args, **kwargs):
        connection.queries_log.clear()  # сбрасываем логи

        self.stdout.write(self.style.SUCCESS("Создание пользователей..."))
        managers, employees = self.create_users()
        users = managers + employees

        self.stdout.write(self.style.SUCCESS("Создание тегов..."))
        tags = self.create_tags(users)

        self.stdout.write(self.style.SUCCESS("Создание задач..."))
        tasks = self.create_tasks(users, tags)

        self.stdout.write(self.style.SUCCESS("Создание проектов..."))
        self.create_projects(managers, employees, tasks)

        self.stdout.write(self.style.SUCCESS("Создание отзывов..."))
        self.create_feedbacks()

        self.stdout.write(self.style.SUCCESS("✅ Генерация данных завершена."))

        if connection.queries:
            print_queries(connection.queries)

    def create_users(self):
        managers = []
        employees = []
        for _ in range(NUM_MANAGERS):
            user = CustomUser.objects.create_user(
                username=fake.user_name(),
                email=fake.email(),
                fio=fake.name(),
                password='password',
                role='manager'
            )
            managers.append(user)

        for _ in range(NUM_EMPLOYEES):
            user = CustomUser.objects.create_user(
                username=fake.user_name(),
                email=fake.email(),
                fio=fake.name(),
                password='password',
                role='employee'
            )
            employees.append(user)
        return managers, employees

    def create_tags(self, users):
        tags = []
        for _ in range(NUM_TAGS):
            tag = TaskTag.objects.create(
                title=fake.word(),
                user=random.choice(users)
            )
            tags.append(tag)
        return tags

    def create_tasks(self, users, tags):
        tasks = []
        for _ in range(NUM_TASKS):
            creator = random.choice(users)
            task = Task.objects.create(
                title=fake.sentence(nb_words=4),
                description=fake.text(max_nb_chars=200),
                priority=random.choice([1, 2, 3]),
                deadline=timezone.now() + timedelta(days=random.randint(1, 30)),
                user=creator,
                is_done=random.choice([True, False])
            )
            task.tags.set(random.sample(tags, k=random.randint(0, min(3, len(tags)))))
            assigned = random.sample(users, k=random.randint(1, 3))
            for emp in assigned:
                TaskEmployee.objects.create(
                    task=task,
                    employee=emp,
                    date_task_take=timezone.now() - timedelta(days=random.randint(1, 5)),
                    date_task_close=timezone.now() if task.is_done else None
                )
            tasks.append(task)
        return tasks

    def create_projects(self, managers, employees, tasks):
        for _ in range(NUM_PROJECTS):
            project = Project.objects.create(
                title=fake.catch_phrase(),
                description=fake.text(max_nb_chars=200),
                deadline=timezone.now() + timedelta(days=random.randint(10, 60)),
                manager=random.choice(managers),
                is_done=random.choice([True, False])
            )
            project_tasks = random.sample(tasks, k=random.randint(2, 6))
            project.tasks.set(project_tasks)
            project_emps = random.sample(employees, k=random.randint(2, 5))
            project.employees.set(project_emps)

            column = Column.objects.get_or_create(name="Не распределено")[0]
            ColumnProject.objects.get_or_create(project=project, column=column)
            for task in project_tasks:
                ColumnTask.objects.get_or_create(task=task, column=column)

    def create_feedbacks(self):
        for _ in range(NUM_FEEDBACKS):
            FeedBack.objects.create(
                name=fake.first_name(),
                last_name=fake.last_name(),
                email=fake.email(),
                phone=fake.phone_number(),
                message=fake.text(max_nb_chars=300)
            )