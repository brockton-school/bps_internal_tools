"""remove foreign key constraint on grade_sections.reference_course_id

Revision ID: 1e712630f869
Revises: 4b5a4cc6e987
Create Date: 2025-04-20 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "1e712630f869"
down_revision = "4b5a4cc6e987"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("grade_sections") as batch_op:
        batch_op.drop_constraint("grade_sections_ibfk_1", type_="foreignkey")


def downgrade():
    with op.batch_alter_table("grade_sections") as batch_op:
        batch_op.create_foreign_key(
            "grade_sections_ibfk_1",
            "courses",
            ["reference_course_id"],
            ["course_id"],
            ondelete="SET NULL",
        )