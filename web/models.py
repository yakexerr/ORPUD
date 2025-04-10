from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()



class Task(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')

    deadline = models.DateTimeField(null=True, blank=True)
    estimated_time = models.DurationField()  # Время на выполнение

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('on_hold', 'On Hold'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    # Дополнительные поля
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    employee = models.ForeignKey('Employee', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    project = models.ForeignKey('Project', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.title


class Employee(models.Model):
    full_name = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    week_hours = models.IntegerField()
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)


class TaskLog(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True)
    old_status = models.CharField(max_length=20)
    new_status = models.CharField(max_length=20)
    changed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Task {self.task.id} status changed from {self.old_status} to {self.new_status}"


class Assignment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    assigned_time = models.FloatField()  # Время, затраченное на выполнение
    assigned_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.employee.full_name} assigned to {self.task.title}"


class TimeSlot(models.Model):
    title = models.CharField(max_length=256)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_realtime = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.title} ({self.start_date} - {self.end_date})"



class Project(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    def __str__(self):
        return self.name


