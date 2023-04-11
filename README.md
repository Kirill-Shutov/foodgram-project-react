## Учебный проект Foodgram.

![example workflow](https://github.com/Kirill-Shutov/foodgram-project-react/actions/workflows/foodgram-project-react_workflow.yml/badge.svg)

### Техническое описание проекта Foodgram. ###

Проект **Foodgram** позволяет постить рецепты, подписываться на авторов, добавлять рецепты в избранное и скачивать списки продуктов.

### Технологии:
* Django
* Python
* Docker
* nginx
* PostgreSQL

### Установка и запуск проекта:

* Клонировать репозиторий и перейти в него в командной строке:

```bash
git clone https://github.com/Kirill-Shutov/foodgram-project-react.git

```

* Подготовьте сервер:

```
scp docker-compose.yml <username>@<host>:/home/<username>/
scp nginx.conf <username>@<host>:/home/<username>/
scp .env <username>@<host>:/home/<username>/
```

* Установите docker и docker-compose:

```
sudo apt install docker.io
sudo apt install docker-compose
```

* Соберите контейнер и выполните миграции:

```
sudo docker-compose up -d --build
sudo docker-compose exec backend python manage.py migrate
```

* Создайте суперюзера и соберите статику:

```
sudo docker-compose exec backend python manage.py createsuperuser
sudo docker-compose exec backend python manage.py collectstatic --no-input
```

* Данные для проверки работы приложения: Суперпользователь

```
email: admin@admin.ru
pass: 739422
```


Документация:
Документацию к проекту можно посмотреть на странице api/docs. Администрирование доступно на странице /admin.


### Автор:
Шутов Кирилл. Задание было выполнено с божьей помощью.

Server address:
158.160.37.246
