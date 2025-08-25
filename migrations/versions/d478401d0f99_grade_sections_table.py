"""add grade_sections table"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'd478401d0f99'
down_revision: Union[str, Sequence[str], None] = '2c1a50c4c187'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'grade_sections',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('display_name', sa.String(length=255), nullable=False),
        sa.Column('school_level', sa.String(length=64), nullable=True),
        sa.Column('reference_course_id', sa.String(length=32), nullable=True),
        sa.ForeignKeyConstraint(['reference_course_id'], ['courses.course_id'], ondelete='SET NULL'),
        sa.UniqueConstraint('display_name')
    )


def downgrade() -> None:
    op.drop_table('grade_sections')