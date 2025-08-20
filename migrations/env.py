import os
import sys
from pathlib import Path
from alembic import context
from sqlalchemy import engine_from_config, pool
import importlib.util
import types

# Ensure project root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[1]

# Create minimal package to satisfy relative imports
pkg = types.ModuleType("bps_internal_tools")
sys.modules["bps_internal_tools"] = pkg

# Load extensions module
ext_spec = importlib.util.spec_from_file_location(
    "bps_internal_tools.extensions", PROJECT_ROOT / "bps_internal_tools" / "extensions.py"
)
extensions = importlib.util.module_from_spec(ext_spec)
ext_spec.loader.exec_module(extensions)
sys.modules["bps_internal_tools.extensions"] = extensions

# Load models module
models_spec = importlib.util.spec_from_file_location(
    "bps_internal_tools.models", PROJECT_ROOT / "bps_internal_tools" / "models.py"
)
models = importlib.util.module_from_spec(models_spec)
models_spec.loader.exec_module(models)
Base = models.Base

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
