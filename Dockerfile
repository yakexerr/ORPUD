# Dockerfile
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Копируем сначала только файл с зависимостями
COPY requirements.txt .

# Устанавливаем зависимости (если requirements.txt не менялся — слой закэшируется)
RUN pip install --no-cache-dir --default-timeout=1000 --retries=10 -r requirements.txt

COPY . .

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]