"""Add user and role lookup indexes.

Revision ID: 4ea7c6439871
Revises: cc90f087a0ae
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "4ea7c6439871"
down_revision: Union[str, Sequence[str], None] = "cc90f087a0ae"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_unique_constraint("uq_users_email", "users", ["email"])
    op.create_unique_constraint("uq_roles_name", "roles", ["name"])
    op.create_unique_constraint(
        "uq_user_roles_user_role", "user_roles", ["user_id", "role_id"]
    )
    op.create_index(
        "ix_users_active_created_id",
        "users",
        ["created_at", "id"],
        postgresql_where=sa.text("deleted_at IS NULL"),
    )
    op.create_index("ix_user_roles_role_user", "user_roles", ["role_id", "user_id"])


def downgrade() -> None:
    op.drop_index("ix_user_roles_role_user", table_name="user_roles")
    op.drop_index("ix_users_active_created_id", table_name="users")
    op.drop_constraint("uq_user_roles_user_role", "user_roles", type_="unique")
    op.drop_constraint("uq_roles_name", "roles", type_="unique")
    op.drop_constraint("uq_users_email", "users", type_="unique")
