"""add grade column to users_canvas

Revision ID: 2c1a50c4c187
Revises: 5d6404a5bcaf
Create Date: 2025-08-29 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "2c1a50c4c187"
down_revision = "5d6404a5bcaf"
branch_labels = None
depends_on = None

def upgrade():
    with op.batch_alter_table("users_canvas") as batch_op:
        batch_op.add_column(sa.Column("grade", sa.String(length=64), nullable=True))

def downgrade():
    with op.batch_alter_table("users_canvas") as batch_op:
        batch_op.drop_column("grade")