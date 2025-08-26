"""add import logging and timestamps to users_canvas

Revision ID: 3b5f9b8b2c6d
Revises: d478401d0f99
Create Date: 2025-10-27 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "3b5f9b8b2c6d"
down_revision = "d478401d0f99"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("users_canvas") as batch_op:
        batch_op.add_column(sa.Column("updated_at", sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column("status_changed_at", sa.DateTime(), nullable=True))

    op.create_table(
        "user_imports",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("imported_at", sa.DateTime(), nullable=False),
    )

    op.create_table(
        "user_change_logs",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("import_id", sa.Integer(), sa.ForeignKey("user_imports.id", ondelete="CASCADE"), nullable=True),
        sa.Column("user_id", sa.String(length=64), nullable=False),
        sa.Column("field", sa.String(length=64), nullable=False),
        sa.Column("old_value", sa.Text(), nullable=True),
        sa.Column("new_value", sa.Text(), nullable=True),
        sa.Column("changed_at", sa.DateTime(), nullable=False),
    )


def downgrade():
    op.drop_table("user_change_logs")
    op.drop_table("user_imports")
    with op.batch_alter_table("users_canvas") as batch_op:
        batch_op.drop_column("status_changed_at")
        batch_op.drop_column("updated_at")