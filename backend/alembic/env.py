from logging.config import fileConfig

from sqlalchemy import create_engine, pool

from alembic import context
from app.auth.models import (
    AuthSession,  # noqa: F401  (register models on Base.metadata)
)
from app.config import settings
from app.models import Base
from app.sensors.models import Sensor  # noqa: F401
from app.users.models import User  # noqa: F401

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata
url = settings.SQLALCHEMY_DATABASE_URI


def run_migrations_offline() -> None:
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = create_engine(url, poolclass=pool.NullPool)
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
