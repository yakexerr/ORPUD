from django.db import models
from django.contrib.auth import get_user_model

class Task(models.Model):  # не просто класс, а именно модель
    # primary key не добавляем (django добавит автоматически)
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
