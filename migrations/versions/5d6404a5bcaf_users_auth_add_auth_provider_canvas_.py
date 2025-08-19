"""users_auth add auth_provider + canvas_user_id

Revision ID: 5d6404a5bcaf
Revises: 780e729f7b1b
Create Date: 2025-08-18 20:10:19.683681

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "5d6404a5bcaf"
down_revision = "780e729f7b1b"
branch_labels = None
depends_on = None

def upgrade():
    bind = op.get_bind()
    is_sqlite = bind.dialect.name == "sqlite"

    # Use batch_alter_table so add column works on SQLite
    with op.batch_alter_table("users_auth") as batch_op:
        batch_op.add_column(sa.Column("auth_provider", sa.String(length=32), nullable=True))
        batch_op.add_column(sa.Column("canvas_user_id", sa.String(length=64), nullable=True))

        # Only create the FK when not SQLite (works on MariaDB/MySQL)
        if not is_sqlite:
            batch_op.create_foreign_key(
                "fk_users_auth_canvas_user",
                "users_canvas",
                ["canvas_user_id"],
                ["user_id"],
                ondelete="SET NULL",
            )
            
def downgrade():
    bind = op.get_bind()
    is_sqlite = bind.dialect.name == "sqlite"

    # Drop FK only if it exists (i.e., non-SQLite path)
    if not is_sqlite:
        op.drop_constraint("fk_users_auth_canvas_user", "users_auth", type_="foreignkey")

    with op.batch_alter_table("users_auth") as batch_op:
        batch_op.drop_column("canvas_user_id")
        batch_op.drop_column("auth_provider")