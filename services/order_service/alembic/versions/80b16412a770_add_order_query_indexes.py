"""Add indexes for order list and relationship queries.

Revision ID: 80b16412a770
Revises: ec6a8f15f7d3
"""
from typing import Sequence, Union

from alembic import op


revision: str = "80b16412a770"
down_revision: Union[str, Sequence[str], None] = "ec6a8f15f7d3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index("ix_orders_created_id", "orders", ["created_at", "id"])
    op.create_index(
        "ix_orders_status_created_id", "orders", ["status", "created_at", "id"]
    )
    op.create_index(
        "ix_orders_user_created_id", "orders", ["user_id", "created_at", "id"]
    )
    op.create_index("ix_order_items_order_id", "order_items", ["order_id"])


def downgrade() -> None:
    op.drop_index("ix_order_items_order_id", table_name="order_items")
    op.drop_index("ix_orders_user_created_id", table_name="orders")
    op.drop_index("ix_orders_status_created_id", table_name="orders")
    op.drop_index("ix_orders_created_id", table_name="orders")
