import asyncio
import os
from logging.config import fileConfig
from alembic import context
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

from app.core.database import Base
import app.modules.cart.models
import app.modules.products.models
import app.users.models
import app.modules.orders.models
import app.modules.category.models


config = context.config
fileConfig(config.config_file_name)

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set")

DATABASE_URL = DATABASE_URL.replace(
    "postgresql+asyncpg",
    "postgresql+psycopg2"
)

target_metadata = Base.metadata


def run_migrations_online():
    engine = create_engine(DATABASE_URL)

    with engine.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
    )
    with context.begin_transaction():
        context.run_migrations()
else:
    run_migrations_online()
