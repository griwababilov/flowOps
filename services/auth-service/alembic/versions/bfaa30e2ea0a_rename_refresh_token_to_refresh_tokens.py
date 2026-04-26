"""rename refresh_token to refresh_tokens

Revision ID: bfaa30e2ea0a
Revises: 7cb8cb2761c4
Create Date: 2026-04-26 17:57:47.298775

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bfaa30e2ea0a'
down_revision: Union[str, Sequence[str], None] = '7cb8cb2761c4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.rename_table("refresh_token", "refresh_tokens")


def downgrade() -> None:
    op.rename_table("refresh_tokens", "refresh_token")