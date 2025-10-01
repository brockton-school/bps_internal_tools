"""add user type column

Revision ID: b83e4cd73e76
Revises: f10a3a0e9d0e
Create Date: 2025-09-27 15:01:39.587297

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b83e4cd73e76'
down_revision: Union[str, Sequence[str], None] = 'f10a3a0e9d0e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    with op.batch_alter_table("users_canvas") as batch_op:
        batch_op.add_column(sa.Column("user_type", sa.String(length=64), nullable=True))

def downgrade():
    with op.batch_alter_table("users_canvas") as batch_op:
        batch_op.drop_column("user_type")
