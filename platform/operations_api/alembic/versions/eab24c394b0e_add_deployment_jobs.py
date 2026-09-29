"""Add asynchronous deployment job records.

Revision ID: eab24c394b0e
Revises: b4a093fd6f11
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "eab24c394b0e"
down_revision: Union[str, Sequence[str], None] = "b4a093fd6f11"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "deployments",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("service_id", sa.UUID(), nullable=False),
        sa.Column("target_version", sa.String(length=100), nullable=False),
        sa.Column("idempotency_key", sa.String(length=128), nullable=False),
        sa.Column("state", sa.String(length=20), nullable=False),
        sa.Column("attempts", sa.Integer(), nullable=False),
        sa.Column("error", sa.String(length=1000), nullable=True),
        sa.Column("execution_mode", sa.String(length=40), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["service_id"], ["services.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("idempotency_key", name="uq_deployments_idempotency_key"),
    )
    op.create_index("ix_deployments_state_created", "deployments", ["state", "created_at"])


def downgrade() -> None:
    op.drop_index("ix_deployments_state_created", table_name="deployments")
    op.drop_table("deployments")