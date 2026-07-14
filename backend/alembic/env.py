from logging.config import fileConfig

from sqlalchemy import create_engine, pool

import app.models.debrief  # noqa: F401
import app.models.dna  # noqa: F401
import app.models.session  # noqa: F401
import app.models.subscription_event  # noqa: F401
import app.models.track  # noqa: F401
import app.models.user  # noqa: F401
from alembic import context
from app.config import settings

# Import all models so Alembic can detect them
from app.database import Base

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

# Deliberately NOT routed through config.set_main_option("sqlalchemy.url", ...):
# configparser treats "%" as interpolation syntax, which breaks on a
# percent-encoded password (e.g. "%2A"). Using settings.database_url directly
# below avoids that entirely.


def run_migrations_offline() -> None:
    context.configure(
        url=settings.database_url, target_metadata=target_metadata, literal_binds=True
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = create_engine(settings.database_url, poolclass=pool.NullPool)
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
