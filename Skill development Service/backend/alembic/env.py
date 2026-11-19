import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Add application directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.models import Base
target_metadata = Base.metadata

def get_url():
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        db_user = os.getenv("MYSQL_USER", "nagriksetu_skill")
        db_pass = os.getenv("MYSQL_PASSWORD", "skill-app-pass-2026")
        db_host = os.getenv("MYSQL_HOST", "127.0.0.1")
        db_port = os.getenv("MYSQL_PORT", "3308")
        db_name = os.getenv("MYSQL_DATABASE", "skill_db")
        db_url = f"mysql+pymysql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
    return db_url

def run_migrations_offline() -> None:
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    configuration = config.get_section(config.config_ini_section) or {}
    configuration["sqlalchemy.url"] = get_url()
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
