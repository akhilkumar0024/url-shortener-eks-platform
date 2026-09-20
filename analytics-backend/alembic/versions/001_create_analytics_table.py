"""create analytics table

Revision ID: 001_analytics_clicks
Revises: 
Create Date: 2026-09-17 07:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "001_analytics_clicks"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "analytics",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("short_code", sa.String(length=32), nullable=False),
        sa.Column("clicked_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("referrer", sa.Text(), nullable=True),
        sa.Column("user_agent", sa.Text(), nullable=True),
        sa.Column("client_ip", sa.Text(), nullable=True),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_analytics_short_code"), "analytics", ["short_code"], unique=False)
    op.create_index(op.f("ix_analytics_clicked_at"), "analytics", ["clicked_at"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_analytics_clicked_at"), table_name="analytics")
    op.drop_index(op.f("ix_analytics_short_code"), table_name="analytics")
    op.drop_table("analytics")
