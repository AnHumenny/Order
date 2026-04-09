## Структура модуля

### backend

```
Project/
├── app/
│   ├── core/                              # Ядро приложения
│   │   ├── config.py                      # Конфигурация (настройки, переменные окружения)
│   │   ├── database.py                    # Подключение к БД, сессии
│   │   ├── dependencies.py                # Общие зависимости (пагинация, auth)
│   │   └── security.py                    # Хеширование паролей, JWT токены
│   │
│   ├── modules/                           # Модули приложения (функциональные блоки)
│   │   │
│   │   ├── admin/                         # Административная панель
│   │   │   ├── __init__.py                # Инициализация и экспорт admin
│   │   │   ├── config.py                  # Настройки админ-панели
│   │   │   ├── auth.py                    # Настройка доступа к админке
│   │   │   └── views/                     # Представления для разных моделей
│   │   │       ├── __init__.py
│   │   │       ├── users.py               # AdminView для пользователей
│   │   │       ├── products.py            # AdminView для товаров
│   │   │       ├── orders.py              # AdminView для заказов
│   │   │       ├── categories.py          # AdminView для категорий
│   │   │       └── dashboard.py           # AdminView дашбоард
│   │   │
│   │   ├── analytics/                     # Аналитика и статистика
│   │   │   ├── __init__.py
│   │   │   ├── models.py                  # Модели аналитики
│   │   │   ├── schemas.py                 # Pydantic схемы
│   │   │   ├── repository.py              # Запросы к БД для аналитики
│   │   │   ├── service.py                 # Бизнес-логика аналитики
│   │   │   └── router.py                  # Эндпоинты (/analytics/...)
│   │   │
│   │   ├── auth/                          # Аутентификация и пользователи
│   │   │   ├── __init__.py                # Инициализация модуля, экспорт роутера
│   │   │   ├── models.py                  # SQLAlchemy модели (User)
│   │   │   ├── schemas.py                 # Pydantic схемы для валидации
│   │   │   ├── repository.py              # CRUD-операции с БД
│   │   │   ├── service.py                 # Бизнес-логика (регистрация, логин)
│   │   │   ├── router.py                  # FastAPI эндпоинты
│   │   │   └── dependencies.py            # Зависимости (get_current_user)
│   │   │
│   │   ├── cart/                          # Корзина покупок
│   │   │   ├── __init__.py
│   │   │   ├── models.py                  # Модель корзины
│   │   │   ├── schemas.py                 # Pydantic схемы
│   │   │   ├── repository.py              # Работа с БД
│   │   │   ├── service.py                 # Логика корзины
│   │   │   └── router.py                  # Эндпоинты (/cart/...)
│   │   │
│   │   ├── category/                      # Категории товаров
│   │   │   ├── __init__.py
│   │   │   ├── models.py                  # Модель категории
│   │   │   ├── schemas.py                 # Pydantic схемы
│   │   │   ├── repository.py              # Запросы к БД
│   │   │   ├── service.py                 # Бизнес-логика
│   │   │   └── router.py                  # Эндпоинты (/categories/...)
│   │   │
│   │   ├── orders/                        # Заказы
│   │   │   ├── __init__.py
│   │   │   ├── models.py                  # Модели заказов
│   │   │   ├── schemas.py                 # Pydantic схемы
│   │   │   ├── repository.py              # Работа с БД
│   │   │   ├── service.py                 # Логика заказов
│   │   │   └── router.py                  # Эндпоинты (/orders/...)
│   │   │
│   │   ├── payment/                       # Платежи (Stripe)
│   │   │   ├── __init__.py
│   │   │   ├── models.py                  # Модели платежей
│   │   │   ├── schemas.py                 # Pydantic схемы
│   │   │   ├── repository.py              # Работа с БД
│   │   │   ├── service.py                 # Логика платежей
│   │   │   ├── router.py                  # Эндпоинты (/payment/...)
│   │   │   └── stripe_client.py           # Интеграция со Stripe
│   │   │
│   │   ├── products/                      # Товары
│   │   │   ├── __init__.py
│   │   │   ├── models.py                  # Модели товаров
│   │   │   ├── schemas.py                 # Pydantic схемы
│   │   │   ├── repository.py              # Запросы к БД
│   │   │   ├── service.py                 # Бизнес-логика
│   │   │   ├── router.py                  # Эндпоинты (/products/...)
│   │   │   └── gallery/                   # Галерея изображений
│   │   │       ├── __init__.py
│   │   │       ├── models.py              # Модели галереи
│   │   │       ├── schemas.py             # Pydantic схемы
│   │   │       ├── repository.py          # Работа с БД
│   │   │       ├── service.py             # Логика галереи
│   │   │       ├── router.py              # API эндпоинты
│   │   │       └── upload.py              # Логика загрузки файлов
│   │   │
│   │   └── users/                         # Пользователи (расширенный профиль)
│   │       ├── __init__.py
│   │       ├── models.py                  # Модель пользователя
│   │       ├── schemas.py                 # Pydantic схемы
│   │       ├── repository.py              # Работа с БД
│   │       ├── service.py                 # Логика пользователей
│   │       ├── dependencies.py            # Зависимости (get_current_user)
│   │       └── router.py                  # Эндпоинты (/users/...)
│   │
│   └── main.py                            # Точка входа, подключение роутеров
│
├── alembic/                               # Миграции БД
├── .env                                   # Переменные окружения
├── .gitignore
├── alembic.ini
└── requirements.txt
```

### Функционал

```
| Модуль | Описание | Основные эндпоинты |
|--------|----------|-------------------|
| **Admin** | Панель управления |
| **Auth** | Модель пользователя, регистрация, обновление, удаление пользвоателя |
| **Users** | Профили | Аутентификация, текущий пользователь | `GET /users/me` |
| **Products** | Управление товарами | `GET /products`, `GET /products/{id}`, `POST /products` (admin) |
| **Categories** | Категории товаров | `GET /categories`, `GET /categories/{id}/products` |
| **Cart** | Корзина покупок | `GET /cart`, `POST /cart/add`, `DELETE /cart/remove/{item_id}` |
| **Orders** | Оформление и история заказов | `POST /orders`, `GET /orders`, `GET /orders/{id}` |
| **Payment** | Интеграция со Stripe | `POST /payment/create-checkout-session`, `POST /payment/webhook` |
| **Analytics** | Статистика покупок | `GET /analytics/user-purchases`, `GET /analytics/user-stats` |
```

### Технологии
```
- **FastAPI** — веб-фреймворк
- **PostgreSQL** — база данных
- **SQLAlchemy 2.0** — ORM
- **Alembic** — миграции
- **JWT** — аутентификация
- **Stripe** — платежи
- **Pydantic** — валидация данных
```

----------------------------------------------------
----------------------------------------------------
### React + TypeScript + Vite

[![YouTube](https://img.shields.io/badge/YouTube-Видео_обзор-FF0000?style=for-the-badge&logo=youtube&logoColor=white)](https://www.youtube.com/watch?v=4XtMk9m5ymI)