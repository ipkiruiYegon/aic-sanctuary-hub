from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import os
from dotenv import load_dotenv
from sqlmodel import SQLModel

# Import your models here to register them with Alembic
from app.db import models

# Load environment variables
load_dotenv()

# Alembic Config object
config = context.config

# Override sqlalchemy.url with DATABASE_URL from .env
database_url = os.getenv("SQLALCHEMY_URL")
if database_url:
    config.set_main_option("sqlalchemy.url", database_url)

# Logging setup
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Import your models
target_metadata = SQLModel.metadata


def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    context.configure(
        url=config.get_main_option("sqlalchemy.url"),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection,
                          target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
