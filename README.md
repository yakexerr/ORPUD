# Task Management System

# Task Management System

## 📌 Описание проекта
Task Management System — это платформа для управления задачами сотрудников.  
Позволяет назначать задачи, следить за загруженностью сотрудников и анализировать прогресс.

## 🚀 Основные возможности
- 📋 **Управление задачами**: создание, редактирование, удаление задач.
- 👥 **Распределение задач**: назначение задач сотрудникам.
- 📊 **Анализ нагрузки**: контроль за перегрузкой сотрудников.
- 📜 **Логирование изменений**: отслеживание всех изменений в задачах.

## 🛠️ Технологии
- **Backend**: Python
- **Database**: PostgreSQL
- **ORM**: Entity Framework

## 📦 Установка и запуск
### Клонирование репозитория
```sh
git clone https://github.com/yakexerr/ORPUD.git
cd task-management
```
## 🌠 Запуск проекта для разработки
- `python -m venv venv` - создание виртуального окружения
- `venv\Scripts\activate` - войти в виртуальное окружение
- `pip install -r requirements.txt` - установка зависимостей
- `python manage.py migrate` - применение миграций
- `python manage.py runserver` - запустить сервер для разработки на http://127.0.0.1:8000

## 🐳 Шаги для запуска Django с PostgreSQL в Docker

### 1. Подготовка

- Linux - Docker и Docker Compose.
- Window - [Docker Desktop](https://www.docker.com/products/docker-desktop/) (тут же установятся и Docker с Docker Compose).

!!! На windows запустите Docker Desktop

### 2. Сборка и запуск контейнеров с помощью Docker Compose

Сначала выполните сборку контейнеров:

```bash
docker-compose build
```

Затем запустите контейнеры:

```bash
docker-compose up -d
```

Контейнеры для Django и PostgreSQL будут запущены и будут доступны по следующим адресам:

- Django: `http://localhost:8000`
- PostgreSQL: `localhost:5432`

### 3. Применение миграций

После того как контейнеры запустятся, вам нужно применить миграции для базы данных. Выполните команду для применения миграций внутри контейнера с Django:

```bash
docker exec -it orpud-web-1 python manage.py makemigrations
docker exec -it orpud-web-1 python manage.py migrate
```

### 4. (Опционально) Создание суперпользователя

Если вам нужно создать суперпользователя для административной панели Django, выполните следующую команду:

```bash
docker exec -it orpud-web-1 python manage.py createsuperuser
```

Следуйте инструкциям на экране, чтобы указать имя пользователя, email и пароль для суперпользователя.

### 5. Запуск сервера

Если сервер не был автоматически запущен, вы можете запустить его вручную с помощью следующей команды:

```bash
docker exec -it orpud-web-1 python manage.py runserver 0.0.0.0:8000
```

Теперь сервер Django будет доступен по адресу `http://localhost:8000`.

---

## Дополнительные команды Docker

### Просмотр состояния контейнеров

Чтобы проверить, что контейнеры работают, используйте команду:

```bash
docker ps
```

### Остановка контейнеров

Чтобы остановить контейнеры, выполните:

```bash
docker-compose down
```

---

## Команды для работы с базой данных

### Выгрузка данных из базы данных в файл

Для того чтобы выгрузить данные из базы данных PostgreSQL в файл (например, в формат SQL), выполните команду:

```bash
docker exec -it orpud-db-1 pg_dump -U laba2_user -d laba2_db -f /var/lib/postgresql/data/laba2_db_dump.sql
```

Эта команда создаст файл `laba2_db_dump.sql` в контейнере PostgreSQL.

Затем, чтобы скопировать файл из контейнера на локальную машину, выполните команду:

```bash
docker cp orpud-db-1:/var/lib/postgresql/data/laba2_db_dump.sql ./laba2_db_dump.sql
```

### Загрузка данных в базу данных из файла

Для того чтобы загрузить данные из ранее выгруженного файла в базу данных PostgreSQL, выполните команду:

```bash
docker cp ./laba2_db_dump.sql orpud-db-1:/var/lib/postgresql/data/laba2_db_dump.sql
```

После этого, выполните команду внутри контейнера PostgreSQL, чтобы загрузить данные:

```bash
docker exec -it orpud-db-1 psql -U laba2_user -d laba2_db -f /var/lib/postgresql/data/laba2_db_dump.sql
```


## 🔄 Git: Работа с веткой master и текущей веткой

## 📥 1. Загрузка ветки `origin/master` в локальный `master`

```bash
git fetch origin
```
```bash
git checkout master
```
```bash
git reset --hard origin/master
```

> 💡 `reset --hard` перезаписывает локальную ветку `master` последним состоянием удалённой ветки `origin/master`.

---

## 🔀 2. Слияние текущей ветки с `master`

```bash
git merge <название-текущей-ветки>
```

> 💡 Замените `your-feature-branch` на имя вашей рабочей ветки.

---

## 🚀 3. Пуш ветки `master` в `origin/master`

```bash
git push origin master
```

> ⚠️ Убедитесь, что в `master` только нужные изменения.

---

## 💾 * Коммит изменений в текущую ветку

```bash
git add .
git commit -m "Краткое описание изменений"
git push origin your-feature-branch
```

> 📝 Замените `your-feature-branch` на имя вашей текущей ветки.  
> Используйте осмысленные сообщения коммита, например:  
> `Fix: обработка ошибок при логине`  
> `Feat: добавлен фильтр задач`

---

## 🛠 Полезные команды

```bash
git branch                   # список локальных веток
git status                   # текущее состояние файлов
git log --oneline --graph    # визуализация истории коммитов
```

---

## ✅ Пример полного сценария

```bash
git fetch origin
git checkout master
git reset --hard origin/master

git checkout your-feature-branch
git merge master

git checkout master
git push origin master
```
