Находясь в папке infra, выполните команду docker-compose up. При выполнении этой команды контейнер frontend, описанный в docker-compose.yml, подготовит файлы, необходимые для работы фронтенд-приложения, а затем прекратит свою работу.

По адресу http://localhost изучите фронтенд веб-приложения, а по адресу http://localhost/api/docs/ — спецификацию API.

По адресу http://158.160.6.84 можно перейти на сам сайт

# Foodgram - «Продуктовый помощник»

## Описание проекта

Foodgram - это онлайн-сервис для публикации рецептов. Пользователи могут:
- Создавать собственные рецепты
- Подписываться на других авторов
- Добавлять рецепты в избранное
- Формировать список покупок для выбранных рецептов
- Скачивать список продуктов в формате txt

## Технологии

- **Backend**: Django REST Framework
- **Frontend**: React
- **База данных**: PostgreSQL
- **Веб-сервер**: Nginx
- **Контейнеризация**: Docker
- **CI/CD**: GitHub Actions

## Запуск проекта (развертывание на сервере)

# Сборка и запуск контейнеров в фоновом режиме
docker-compose up -d --build

# Выполнение миграций
docker-compose exec backend python manage.py migrate

# Создание суперпользователя
docker-compose exec backend python manage.py createsuperuser

# Сбор статики
docker-compose exec backend python manage.py collectstatic --noinput

# Загрузка тестовых данных (опционально)
docker-compose exec backend python manage.py loaddata fixtures.json


# Аутентификация

POST /api/auth/token/login/
Content-Type: application/json

{
    "email": "user@example.com",
    "password": "yourpassword123"
}

# Ответ:
{
    "auth_token": "ваш_токен_авторизации"
}

# Пользователи

GET /api/users/
Authorization: Token ваш_токен

# Ответ (список пользователей):
{
    "count": 10,
    "next": null,
    "previous": null,
    "results": [
        {
            "email": "user1@example.com",
            "id": 1,
            "username": "user1",
            "first_name": "Иван",
            "last_name": "Иванов"
        },
        ...
    ]
}

# Рецепты

# Получение списка с фильтрацией:

GET /api/recipes/?tags=breakfast
Authorization: Token ваш_токен

# Ответ:
{
    "id": 1,
    "tags": [{"id": 1, "name": "Завтрак", "slug": "breakfast"}],
    "author": {"id": 1, "username": "user1"},
    "ingredients": [
        {"id": 1, "name": "Яйца", "measurement_unit": "шт", "amount": 2},
        {"id": 2, "name": "Молоко", "measurement_unit": "мл", "amount": 100}
    ],
    "is_favorited": true,
    "is_in_shopping_cart": false,
    "name": "Омлет",
    "image": "http://example.com/media/recipes/omlet.jpg",
    "text": "Простой рецепт омлета...",
    "cooking_time": 10
}

# Создание рецепта:

POST /api/recipes/
Content-Type: multipart/form-data
Authorization: Token ваш_токен

# Form Data:
name: Спагетти Карбонара
text: Приготовить пасту...
cooking_time: 20
tags: 1,2
ingredients: [{"id": 3, "amount": 200}, {"id": 4, "amount": 100}]
image: (binary file)


# Подписки

GET /api/users/subscriptions/
Authorization: Token ваш_токен

# Ответ:
[
    {
        "id": 2,
        "username": "chef123",
        "email": "chef@example.com",
        "first_name": "Мария",
        "last_name": "Петрова",
        "is_subscribed": true,
        "recipes": [
            {
                "id": 5,
                "name": "Тирамису",
                "image": "http://example.com/media/recipes/tiramisu.jpg",
                "cooking_time": 120
            }
        ],
        "recipes_count": 3
    }
]

# Список покупок

# Добавление рецепта:


POST /api/recipes/{id}/shopping_cart/
Authorization: Token ваш_токен

# Ответ:
{
    "id": 1,
    "name": "Омлет",
    "image": "http://example.com/media/recipes/omlet.jpg",
    "cooking_time": 10
}

# Скачивание списка:

GET /api/recipes/download_shopping_cart/
Authorization: Token ваш_токен
Accept: application/pdf

# Ответ: txt файл с ингредиентами

# Теги и ингредиенты

GET /api/tags/
# Ответ:
[
    {"id": 1, "name": "Завтрак", "color": "#E26C2D", "slug": "breakfast"},
    {"id": 2, "name": "Обед", "color": "#49B64E", "slug": "lunch"}
]

GET /api/ingredients/?name=яй
# Ответ:
[
    {"id": 1, "name": "Яйца", "measurement_unit": "шт"},
    {"id": 5, "name": "Яичный белок", "measurement_unit": "г"}
]

# Управление профилем

PATCH /api/users/me/
Content-Type: application/json
Authorization: Token ваш_токен

{
    "first_name": "Новое имя",
    "last_name": "Новая фамилия"
}

# Ответ:
{
    "email": "user@example.com",
    "id": 1,
    "username": "username",
    "first_name": "Новое имя",
    "last_name": "Новая фамилия"
}

# Автор:
Илья Уткин
почта: utkin-ilia20033@mail.ru