from logging.config import fileConfig
from sqlalchemy.ext.asyncio import create_async_engine
from alembic import context
from app.core.database import Base
from app.core.config import settings

config = context.config
fileConfig(config.config_file_name)

target_metadata = Base.metadata
DATABASE_URL = settings.DATABASE_URL


def run_migrations_offline():
    """Run migrations within the provided connection.

    This helper function is used in offline mode to run migrations
    synchronously through the provided database connection.
    """
    url = DATABASE_URL
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    """Run migrations within the provided connection.

    This helper function is used in online mode to run migrations
    synchronously through the provided database connection."""

    context.configure(connection=connection, target_metadata=target_metadata)


async def run_migrations_online():
    """Run migrations within the provided connection.

    This helper function is used in oline mode to run migrations
    synchronously through the provided database connection.
    """
    connectable = create_async_engine(DATABASE_URL, future=True)

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()

if context.is_offline_mode():
    run_migrations_offline()
else:
    import asyncio
    asyncio.run(run_migrations_online())
