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
│ │ ├── products/ # Товары        # В доработке
│ │ │ ├── schemas.py # Pydantic схемы
│ │ │ ├── repository.py # Запросы к БД
│ │ │ ├── service.py # Бизнес-логика
│ │ │ └── router.py # Эндпоинты (/products/...)
│ │ │
│ │ └── users/ # Пользователи и авторизация
│ │ ├── models.py # Модель пользователя
│ │ ├── schemas.py # Pydantic схемы
│ │ ├── repository.py # Работа с БД
│ │ ├── service.py # Логика пользователей
│ │ ├── dependencies.py # Зависимости (get_current_user)
│ │ └── router.py # Эндпоинты (/users/...)
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
| **Users** | Регистрация, аутентификация, профили | `POST /users/register`, `POST /users/login`, `GET /users/me` |
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

### Структура frontend
```
Project/
│
├── admin/ # Административная панель (в разработке)
│ ├── backend/ # Бэкенд админки
│ └── frontend/ # Фронтенд админки
│
├── client/ # Основное React-приложение
│ ├── .vite/ # Кэш Vite
│ ├── node_modules/ # Зависимости
│ ├── public/ # Статические файлы
│ │ └── vite.svg # Логотип
│ │
│ ├── src/ # Исходный код
│ │ ├── api/ # API клиенты
│ │ │ ├── analytics.ts # Запросы к аналитике
│ │ │ ├── auth.ts # Аутентификация
│ │ │ ├── cart.ts # Корзина
│ │ │ ├── categories.ts # Категории
│ │ │ ├── orders.ts # Заказы
│ │ │ ├── products.ts # Товары
│ │ │ ├── types.ts # TypeScript типы
│ │ │ └── user.ts # Пользователи
│ │ │
│ │ ├── assets/ # Изображения, шрифты
│ │ │
│ │ ├── components/ # Переиспользуемые компоненты
│ │ │ ├── Analytics/ # Компоненты аналитики
│ │ │ ├── CartPage.tsx # Компонент корзины
│ │ │ ├── CategoriesMenu.tsx # Меню категорий
│ │ │ ├── ErrorBoundary.tsx # Обработка ошибок
│ │ │ ├── Input.tsx # Кастомное поле ввода
│ │ │ ├── ProtectedRoute.tsx # Защита маршрутов
│ │ │ ├── SubcategoryList.tsx # Список подкатегорий
│ │ │ └── UserBox.tsx # Блок пользователя
│ │ │
│ │ ├── constants/ # Константы
│ │ │ └── api.ts # URL API
│ │ │
│ │ ├── context/ # React Context
│ │ │ ├── AuthContext.tsx # Авторизация
│ │ │ └── CartContext.tsx # Корзина
│ │ │
│ │ ├── hooks/ # Кастомные хуки
│ │ │ └── useLogout.ts # Выход из системы
│ │ │
│ │ ├── pages/ # Страницы приложения
│ │ │ ├── Cancel.tsx # Отмена оплаты
│ │ │ ├── CartPage.tsx # Корзина
│ │ │ ├── CategoryPages.tsx # Категории
│ │ │ ├── CategoryProductsPage.tsx # Товары категории
│ │ │ ├── HomePage.tsx # Главная
│ │ │ ├── LoginPage.tsx # Вход
│ │ │ ├── OrdersPage.tsx # Заказы
│ │ │ ├── ProductPage.tsx # Товар
│ │ │ ├── SearchPage.tsx # Поиск
│ │ │ ├── Success.tsx # Успешная оплата
│ │ │ └── UserPage.tsx # Личный кабинет
│ │ │
│ │ ├── styles/ # CSS стили
│ │ │ ├── analytics/ # Стили аналитики
│ │ │ ├── auth/ # Стили авторизации
│ │ │ ├── cart/ # Стили корзины
│ │ │ ├── categories/ # Стили категорий
│ │ │ ├── products/ # Стили товаров
│ │ │ ├── user/ # Стили профиля
│ │ │ ├── HomePage.css # Стили главной
│ │ │ └── main.css # Глобальные стили
│ │ │
│ │ ├── utils/ # Вспомогательные функции
│ │ │
│ │ ├── App.css # Корневые стили
│ │ ├── App.tsx # Корневой компонент
│ │ ├── index.css # Базовые стили
│ │ ├── main.tsx # Точка входа
│ │ └── vite-env.d.ts # Типы Vite
│ │
│ ├── .env # Переменные окружения
│ ├── .gitignore # Игнорируемые файлы
│ ├── env_example.txt # Пример .env
│ ├── eslint.config.js # Конфиг ESLint
│ ├── index.html # HTML шаблон
│ ├── package.json # Зависимости
│ ├── package-lock.json # Lock-файл
│ ├── README.md # Документация
│ ├── tsconfig.app.json # TS конфиг для приложения
│ ├── tsconfig.json # Основной TS конфиг
│ ├── tsconfig.node.json # TS конфиг для Node
│ └── vite.config.ts # Конфигурация Vite
│
├── .gitignore # Игнорируемые файлы корня
├── env_example.txt # Пример .env корня
├── package.json # Зависимости корня
├── package-lock.json # Lock-файл корня
└── README.md # Корневая документация

```
 ### Функциональные возможности
```

| Страница | Путь | Описание |
|----------|------|----------|
| **Главная** | `/` | Список товаров, категории |
| **Товар** | `/products/:id` | Детальная информация о товаре |
| **Категория** | `/category/:id` | Товары выбранной категории |
| **Поиск** | `/search?name=...` | Поиск товаров по названию |
| **Корзина** | `/cart` | Просмотр и редактирование корзины |
| **Заказы** | `/orders` | История заказов |
| **Личный кабинет** | `/me` | Профиль и статистика покупок |
| **Вход** | `/login` | Авторизация пользователя |
| **Успех** | `/success` | Подтверждение оплаты |
| **Отмена** | `/cancel` | Отмена оплаты |
```

[![YouTube](https://img.shields.io/badge/YouTube-Видео_обзор-FF0000?style=for-the-badge&logo=youtube&logoColor=white)](https://www.youtube.com/watch?v=JDhCTvHRkEw)