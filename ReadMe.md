### 
Backend для интернет-магазина на FastAPI. Обеспечивает каталог товаров, корзину, оформление заказов, приём платежей (Stripe + YooKassa), аналитику и приватную админ-панель.
----------------------------------------------------
----------------------------------------------------
### React + TypeScript + Vite
[![YouTube]]
----------------------------------------------------

## Architecture

Проект построен по слоистой архитектуре (Layered Architecture) с чётким разделением ответственности:

- **`router.py`** — HTTP-слой (эндпоинты, валидация через Pydantic, зависимости).
- **`service.py`** — бизнес-логика (правила, транзакции, вызовы репозиториев).
- **`repository.py`** — слой доступа к данным (SQLAlchemy-запросы).
- **`models.py`** — ORM-модели (таблицы БД).
- **`schemas.py`** — Pydantic-схемы (валидация запросов/ответов).

**Приватные модули** (`private_modules/`) содержат код, доступный только администратору (`administrator/`) и интеграции (`payment/`, `currency/`). Это позволяет изолировать админский API от пользовательского и подключать его отдельно.

----------------------------------------------------
----------------------------------------------------

## Project Structure

### backend

```
.
├── alembic
│   ├── backup_versions/*
│   ├── versions/*
│   ├── env.py
│   ├── README
│   └── script.py.mako
├── app
│   ├── core
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── dependencies.py
│   │   ├── logging_config.py
│   │   ├── rate_limiter.py
│   │   ├── security.py
│   │   └── session.py
│   ├── modules
│   │   ├── analytics
│   │   │   ├── repository.py
│   │   │   ├── router.py
│   │   │   └── service.py
│   │   ├── cart
│   │   │   ├── models.py
│   │   │   ├── repository.py
│   │   │   ├── router.py
│   │   │   ├── schemas.py
│   │   │   └── service.py
│   │   ├── category
│   │   │   ├── models.py
│   │   │   ├── repository.py
│   │   │   ├── router.py
│   │   │   ├── schemas.py
│   │   │   └── service.py
│   │   ├── orders
│   │   │   ├── models.py
│   │   │   ├── repository.py
│   │   │   ├── router.py
│   │   │   ├── schemas.py
│   │   │   └── service.py
│   │   ├── private_modules
│   │   │   ├── administrator
│   │   │   │   ├── repositories
│   │   │   │   │   ├── categories.py
│   │   │   │   │   ├── orders.py
│   │   │   │   │   ├── products.py
│   │   │   │   │   └── users.py
│   │   │   │   ├── routers
│   │   │   │   │   ├── categories.py
│   │   │   │   │   ├── me.py
│   │   │   │   │   ├── orders.py
│   │   │   │   │   ├── products.py
│   │   │   │   │   └── users.py
│   │   │   │   ├── schemas
│   │   │   │   │   ├── categories.py
│   │   │   │   │   ├── orders.py
│   │   │   │   │   ├── products.py
│   │   │   │   │   └── users.py
│   │   │   │   ├── services
│   │   │   │   │   ├── categories.py
│   │   │   │   │   ├── orders.py
│   │   │   │   │   ├── products.py
│   │   │   │   │   └── users.py
│   │   │   │   ├── dependencies.py
│   │   │   │   ├── __init__.py
│   │   │   │   └── router.py
│   │   │   ├── auth
│   │   │   │   ├── dependencies.py
│   │   │   │   ├── __init__.py
│   │   │   │   ├── models.py
│   │   │   │   ├── repository.py
│   │   │   │   ├── router.py
│   │   │   │   ├── schemas.py
│   │   │   │   └── service.py
│   │   │   ├── currency
│   │   │   │   ├── currency.py
│   │   │   │   ├── dependencies.py
│   │   │   │   ├── __init__.py
│   │   │   │   ├── middleware.py
│   │   │   │   ├── repository.py
│   │   │   │   ├── router.py
│   │   │   │   ├── schemas.py
│   │   │   │   └── service.py
│   │   │   ├── payment
│   │   │   │   ├── stripe
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── stripe_client.py
│   │   │   │   │   ├── stripe_router.py
│   │   │   │   │   └── stripe_service.py
│   │   │   │   ├── yookassa
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── yookassa_client.py
│   │   │   │   │   ├── yookassa_router.py
│   │   │   │   │   └── yookassa_service.py
│   │   │   │   └── __init__.py
│   │   │   └── __init__.py
│   │   ├── products
│   │   │   ├── gallery
│   │   │   │   ├── __init__.py
│   │   │   │   ├── models.py
│   │   │   │   ├── repository.py
│   │   │   │   ├── routes.py
│   │   │   │   ├── schemas.py
│   │   │   │   ├── service.py
│   │   │   │   └── upload.py
│   │   │   ├── dependencies.py
│   │   │   ├── __init__.py
│   │   │   ├── models.py
│   │   │   ├── repository.py
│   │   │   ├── router.py
│   │   │   ├── schemas.py
│   │   │   └── service.py
│   │   ├── users
│   │   │   ├── __init__.py
│   │   │   ├── models.py
│   │   │   └── router.py
│   │   └── __init__.py
│   ├── __init__.py
│   └── main.py
├── logs
│   ├── app.log
│   └── yookassa_webhook.log
├── static
│   └── products/*
├── alembic.ini
├── env_example.txt
├── pyproject.toml
├── ReadMe.md
├── requirements.txt
└── yookassa_webhook.log

```

### Features

```
| Module | Description | Endpoints |
| :--- | :--- | :--- |
| **Auth** | Registration, JWT issuance | `POST /users/login`, `POST /users/register` | ...
| **Users** | User profile management | `GET /users/me` | ...
| **Products** | Product catalog | `GET /products`, `GET /products/{id}` | ...
| **Categories** | Product categories tree | `GET /categories`, `GET /categories/{id}/products` | ...
| **Cart** | Shopping cart | `GET /cart`, `POST /cart/add`, `DELETE /cart/remove/{item_id}` | ...
| **Orders** | Order creation and history | `POST /orders/from-cart`, `POST /orders/checkout`, `DELETE /orders/my` | ...
| **Payment** | Stripe & YooKassa integration | `POST /payment/stripe/create-checkout-session`, `POST /payment/yookassa/create-payment` | ...
| **Analytics** | Purchase statistics | `GET /analytics/user-purchases`, `GET /analytics/user-stats` | ...
| **Currency** | Multi-currency support | `GET /currencies/rates`, `GET /currencies/convert`, `GET /currencies/detect` | ...
| **Administrator** | **Admin Control Panel (Private)** | **`GET /api/admin/me`, `GET /api/admin/users`, `GET /api/admin/orders`, `GET /api/admin/products`, `GET /api/admin/categories/tree`** |  ...
| **Gallery** | **Product image management** | **`GET /images/`, `POST /images/upload`, `PATCH /images/{id}`, `POST /images/{id}/set-main`** | ... ```

### Technologies
```
- **FastAPI** — web framework
- **PostgreSQL** — database
- **SQLAlchemy 2.0** — ORM
- **Alembic** — migrations
- **JWT** — authentication
- **Stripe** — payments
- **Pydantic** — data validation
```
