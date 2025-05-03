from django.contrib import admin
from django.apps import apps
from django.contrib.admin.sites import AlreadyRegistered

# Автоматическое добавление моделей для приложения web
app = apps.get_app_config('web')

for model in app.get_models():
    try:
        admin.site.register(model)
    except AlreadyRegistered:
        pass
# TODO: Исправить создание пользователей (пароль не кодируется)