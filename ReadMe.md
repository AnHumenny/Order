## Структура модуля

### backend

```
Project/
├── app/
│ ├── core/ # Ядро приложения
│ │ ├── config.py # Конфигурация (настройки, переменные окружения)
│ │ ├── database.py # Подключение к БД, сессии
│ │ ├── dependencies.py # Общие зависимости (пагинация, auth)
│ │ └── security.py # Хеширование паролей, JWT токены
│ │
│ ├── modules/ # Модули приложения
│ │ ├──admin/* # Панель управления
│ │ │
│ │ ├── auth/* # Регистрация и аутентификация
│ │ │
│ │ ├── analytics/ # Аналитика и статистика
│ │ │ ├── repository.py # Запросы к БД для аналитики
│ │ │ ├── service.py # Бизнес-логика аналитики
│ │ │ └── router.py # Эндпоинты (/analytics/...)
│ │ │
│ │ ├── cart/ # Корзина покупок
│ │ │ ├── models.py # Модель корзины
│ │ │ ├── schemas.py # Pydantic схемы
│ │ │ ├── repository.py # Работа с БД
│ │ │ ├── service.py # Логика корзины
│ │ │ └── router.py # Эндпоинты (/cart/...)
│ │ │
│ │ ├── category/ # Категории товаров
│ │ │ ├── models.py # Модель категории
│ │ │ ├── schemas.py # Pydantic схемы
│ │ │ ├── repository.py # Запросы к БД
│ │ │ ├── services.py # Бизнес-логика
│ │ │ └── router.py # Эндпоинты (/categories/...)
│ │ │
│ │ ├── orders/ # Заказы
│ │ │ ├── models.py # Модели заказов
│ │ │ ├── schemas.py # Pydantic схемы
│ │ │ ├── repository.py # Работа с БД
│ │ │ ├── service.py # Логика заказов
│ │ │ └── router.py # Эндпоинты (/orders/...)
│ │ │
│ │ ├── payment/ # Платежи (Stripe)
│ │ │ ├── stripe_client.py # Интеграция со Stripe
│ │ │ ├── service.py # Логика платежей
│ │ │ └── router.py # Эндпоинты (/payment/...)
│ │ │
│ │ ├── products/ # Товары
│ │ │ ├── gallery/ # Галерея изображений
│ │ │ │ ├── models.py # Модели галереи
│ │ │ │ ├── repository.py # Работа с БД
│ │ │ │ ├── routes.py # API эндпоинты
│ │ │ │ ├── schemas.py # Pydantic схемы
│ │ │ │ ├── service.py # Логика галереи
│ │ │ │ └── upload.py # Логика загрузки файлов
│ │ │ ├── schemas.py # Pydantic схемы
│ │ │ ├── repository.py # Запросы к БД
│ │ │ ├── service.py # Бизнес-логика
│ │ │ └── router.py # Эндпоинты (/products/...)
│ │ │ 
│ │ └── users/ # Пользователи
│ │   ├── models.py # Модель пользователя
│ │   ├── schemas.py # Pydantic схемы
│ │   ├── repository.py # Работа с БД
│ │   ├── service.py # Логика пользователей
│ │   ├── dependencies.py # Зависимости (get_current_user)
│ │   └── router.py # Эндпоинты (/users/...)
│ │
│ └── main.py # Точка входа, подключение роутеров
│
├── alembic/ # Миграции БД
├── .env # Переменные окружения
├── .gitignore
├── alembic.ini
└── requirements.txt
```

### Функционал

```
| Модуль | Описание | Основные эндпоинты |
|--------|----------|-------------------|
| **Admin** | Панель управления
| **Auth** | Регистрация, аутентификация
| **Users** | Профили | `GET /users/me` |
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