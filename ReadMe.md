----------------------------------------------------
----------------------------------------------------
### React + TypeScript + Vite
[![YouTube](https://img.shields.io/badge/YouTube-Video_rewiev-FF0000?style=for-the-badge&logo=youtube&logoColor=white)](https://www.youtube.com/watch?v=MsaDlukeppg)
----------------------------------------------------
----------------------------------------------------

## Project Structure

### backend

```
Project/
├── app/
│   ├── core/                              # Application core
│   │   ├── config.py                      # Configuration (settings, environment variables)
│   │   ├── database.py                    # Database connection, sessions
│   │   ├── dependencies.py                # Common dependencies (pagination, auth)
│   │   ├── rate_limiter.py                # Rate-limiting for endpoints
│   │   ├── security.py                    # Password hashing, JWT tokens
│   │   └── session.py                     # Session cookies
│   │
│   ├── modules/                           # Application modules (functional blocks)
│   │   │
│   │   ├── analytics/                     # Analytics and statistics
│   │   │   ├── __init__.py
│   │   │   ├── models.py                  # Analytics models
│   │   │   ├── schemas.py                 # Pydantic schemas
│   │   │   ├── repository.py              # Database queries for analytics
│   │   │   ├── service.py                 # Analytics business logic
│   │   │   └── router.py                  # Endpoints (/analytics/...)
│   │   │
│   │   ├── cart/                          # Shopping cart
│   │   │   ├── __init__.py
│   │   │   ├── models.py                  # Cart model
│   │   │   ├── schemas.py                 # Pydantic schemas
│   │   │   ├── repository.py              # Database operations
│   │   │   ├── service.py                 # Cart logic
│   │   │   └── router.py                  # Endpoints (/cart/...)
│   │   │
│   │   ├── category/                      # Product categories
│   │   │   ├── __init__.py
│   │   │   ├── models.py                  # Category model
│   │   │   ├── schemas.py                 # Pydantic schemas
│   │   │   ├── repository.py              # Database queries
│   │   │   ├── service.py                 # Business logic
│   │   │   └── router.py                  # Endpoints (/categories/...)
│   │   │
│   │   ├── orders/                        # Orders
│   │   │   ├── __init__.py
│   │   │   ├── models.py                  # Order models
│   │   │   ├── schemas.py                 # Pydantic schemas
│   │   │   ├── repository.py              # Database operations
│   │   │   ├── service.py                 # Order logic
│   │   │   └── router.py                  # Endpoints (/orders/...)
│   │   │
│   │   ├── products/                      # Products
│   │   │   ├── __init__.py
│   │   │   ├── models.py                  # Product models
│   │   │   ├── schemas.py                 # Pydantic schemas
│   │   │   ├── repository.py              # Database queries
│   │   │   ├── service.py                 # Business logic
│   │   │   ├── router.py                  # Endpoints (/products/...)
│   │   │   └── gallery/                   # Image gallery
│   │   │       ├── __init__.py
│   │   │       ├── models.py              # Gallery models
│   │   │       ├── schemas.py             # Pydantic schemas
│   │   │       ├── repository.py          # Database operations
│   │   │       ├── service.py             # Gallery logic
│   │   │       ├── router.py              # API endpoints
│   │   │       └── upload.py              # File upload logic
│   │   │
│   │   ├──  users/                         # Users (extended profile)
│   │   │   ├── __init__.py
│   │   │   ├── models.py                  # User model
│   │   │   ├── schemas.py                 # Pydantic schemas
│   │   │   ├── repository.py              # Database operations
│   │   │   ├── service.py                 # User logic
│   │   │   ├── dependencies.py            # Dependencies (get_current_user)
│   │   │   └── router.py                  # Endpoints (/users/...)
│   │   │
│   │   └── private_modules
│   │       ├── auth/                          # Authentication and users
│   │       │   ├── __init__.py                # Module initialization, router export
│   │       │   ├── models.py                  # SQLAlchemy models (User)
│   │       │   ├── schemas.py                 # Pydantic schemas for validation
│   │       │   ├── repository.py              # CRUD operations with database
│   │       │   ├── service.py                 # Business logic (registration, login)
│   │       │   ├── router.py                  # FastAPI endpoints
│   │       │   └── dependencies.py            # Dependencies (get_current_user)
│   │       │    
│   │       ├── currency/                      # Multi-currency payments
│   │       │   ├── __init__.py                # Module initialization, router export
│   │       │   ├── currency.py                # Currency Constants: List of supported currencies, symbols, flags, names
│   │       │   ├── models.py                  # SQLAlchemy models (exchange currency)
│   │       │   ├── schemas.py                 # Pydantic schemas for validation
│   │       │   ├── middleware.py              # Middleware for determining user currency by headers/IP
│   │       │   ├── repository.py              # CRUD operations with database
│   │       │   ├── service.py                 # Business logic (getting rates, exchange rates, ... )
│   │       │   ├── router.py                  # FastAPI endpoints
│   │       │   └── dependencies.py            # Dependencies (get_country_by_ip, get_user_currency)
│   │       │
│   │       ├── payment/                        # Payment processing
│   │       │   ├── __init__.py                 # Module initialization
│   │       │   │
│   │       │   ├── stripe/                     # Stripe payment provider
│   │       │   │   ├── __init__.py
│   │       │   │   ├── stripe_client.py        # Stripe API client
│   │       │   │   ├── stripe_router.py        # Endpoints (/payment/stripe/...)
│   │       │   │   └── stripe_service.py       # Stripe business logic
│   │       │   │
│   │       │   ├── yookassa/                   # YooKassa payment provider
│   │       │   │   ├── __init__.py
│   │       │   │   ├── yookassa_client.py      # YooKassa API client
│   │       │   │   ├── yookassa_router.py      # Endpoints (/payment/yookassa/...)
│   │       │   │   └── yookassa_service.py     # YooKassa business logic
│   │       │   │
│   │       │   └── __init__.py
│   │       │    
│   │       └── admin/         # Admin dashboard (built-in FastAPI admin interface)
│   │           ├── __init__.py                # Module initialization
│   │           ├── views/                     # Admin view definitions
│   │           │   ├── __init__.py
│   │           │   ├── dashboard.py           # Main admin dashboard view
│   │           │   ├── users.py               # User management views
│   │           │   ├── products.py            # Product management views
│   │           │   ├── categories.py          # Category management views
│   │           │   └── orders.py              # Order management views
│   │           ├── auth.py                    # Admin authentication & access control
│   │           └── config.py                  # Admin interface configuration
│   │
│   └── main.py                            # Entry point, router registration
│
├── static/ 
│      └── gallery/                        # Photogallery        
│
├── alembic/                               # Database migrations
├── .env                                   # Environment variables
├── env_example                            # Example of environment variables
├── .gitignore
├── alembic.ini
└── requirements.txt
```

### Features

```
| Module          | Description                 | Endpoints
|-----------------|-----------------------------|-------------------------------------------------------------|
| **Admin**       | Control panel               | *:8000/admin/
| **Auth**        | User model                  | registration, list of users, delete user	
| **Users**       | Authentication, current user| authorization, current user
| **Products**    | Product management	        | GET /products, GET /products/{id}, POST /products (admin)...
| **Categories**  | Product categories	        | GET /categories, GET /categories/{id}/products...
| **Cart**        | Shopping cart               | GET /cart, POST /cart/add, DELETE /cart/remove/{item_id}...
| **Orders**      | Checkout and order history  | POST /orders, GET /orders, GET /orders/{id}...
| **Payment**     | Stripe integration          | POST /payment/create-checkout-session, POST /payment/webhook
| **Analytics**   | Purchase statistics	        | GET /analytics/user-purchases, GET /analytics/user-stats
| **Currency**    | Multi-currency support      | GET /currencies/rates, GET /currencies/convert, GET /currencies/detect, GET /currencies/supported 
```

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
