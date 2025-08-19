import os
import sys
from pathlib import Path
from alembic import context
from sqlalchemy import engine_from_config, pool

from bps_internal_tools.extensions import db
target_metadata = db.Model.metadata

# Ensure project root is on sys.path, so 'bps_internal_tools' is importable
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Now import ONLY models metadata (avoid importing create_app)
from bps_internal_tools.models import Base  # <- has your declarative base

config = context.config
# Let env variables drive the URL
config.set_main_option("sqlalchemy.url", os.getenv("DATABASE_URL", "sqlite:///app.db"))

target_metadata = Base.metadata

def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    # render_as_batch=True is safe offline too
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        render_as_batch=True,  # <-- add this
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        # Enable batch mode only when using SQLite
        is_sqlite = connection.dialect.name == "sqlite"
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_as_batch=is_sqlite,   # <-- important
        )
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
