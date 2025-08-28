"""add reference_is_section flag to grade_sections

Revision ID: 4b5a4cc6e987
Revises: 3b5f9b8b2c6d
Create Date: 2025-03-10 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "4b5a4cc6e987"
down_revision = "3b5f9b8b2c6d"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("grade_sections") as batch_op:
        batch_op.add_column(
            sa.Column(
                "reference_is_section",
                sa.Boolean(),
                nullable=False,
                server_default=sa.false(),
            )
        )
        batch_op.alter_column("reference_is_section", server_default=None)


def downgrade():
    with op.batch_alter_table("grade_sections") as batch_op:
        batch_op.drop_column("reference_is_section")