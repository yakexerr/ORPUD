from django.core.management.base import BaseCommand
from models import *
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
import joblib

# Модель прогнозирования времены выполнения задач сотрудниками
class Command(BaseCommand):
    help = 'Train model to predict task completion time by employees'

    def handle(self, *args, **kwargs):
        data = []

        for te in TaskEmployee.objects.select_related('task', 'employee'):
            if te.date_task_take and te.date_task_close:
                delta = (te.date_task_close - te.date_task_take).total_seconds() / 3600  # часы
                data.append({
                    'user_id': te.employee.id,
                    'priority': te.task.priority,
                    'time_to_complete': delta
                })

        df = pd.DataFrame(data)
        if df.empty:
            self.stdout.write(self.style.ERROR("Недостаточно данных для обучения модели."))
            return

        X = df[['user_id', 'priority']]
        y = df['time_to_complete']

        model = RandomForestRegressor()
        model.fit(X, y)

        joblib.dump(model, 'task_model.pkl')
        self.stdout.write(self.style.SUCCESS("Модель успешно обучена и сохранена."))
