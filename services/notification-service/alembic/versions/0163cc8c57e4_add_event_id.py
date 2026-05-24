"""add event_id

Revision ID: 0163cc8c57e4
Revises: ef0d7da39b11
Create Date: 2026-05-24 08:17:12.478531

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0163cc8c57e4'
down_revision: Union[str, Sequence[str], None] = 'ef0d7da39b11'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import text
import uuid


def upgrade() -> None:
    # 1. Добавляем колонку сначала nullable=True
    op.add_column(
        "notifications",
        sa.Column("event_id", sa.String(length=36), nullable=True),
    )

    # 2. Заполняем event_id для уже существующих строк
    connection = op.get_bind()

    result = connection.execute(
        text("SELECT id FROM notifications WHERE event_id IS NULL")
    )

    for row in result:
        connection.execute(
            text(
                """
                UPDATE notifications
                SET event_id = :event_id
                WHERE id = :id
                """
            ),
            {
                "event_id": str(uuid.uuid4()),
                "id": row.id,
            },
        )

    # 3. Теперь можно запретить NULL
    op.alter_column(
        "notifications",
        "event_id",
        existing_type=sa.String(length=36),
        nullable=False,
    )

    # 4. Добавляем уникальность
    op.create_unique_constraint(
        "uq_notifications_event_id",
        "notifications",
        ["event_id"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "uq_notifications_event_id",
        "notifications",
        type_="unique",
    )

    op.drop_column("notifications", "event_id")