"""users_auth add canvas_user_id + auth_provider

Revision ID: 780e729f7b1b
Revises: 890451fb40f1
Create Date: 2025-08-18 19:32:02.116910

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '780e729f7b1b'
down_revision: Union[str, Sequence[str], None] = '890451fb40f1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
