"""Add Operations service environment lookup index.

Revision ID: b4a093fd6f11
Revises: b1b4101396cf
"""
from typing import Sequence, Union

from alembic import op


revision: str = "b4a093fd6f11"
down_revision: Union[str, Sequence[str], None] = "b1b4101396cf"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index("ix_services_environment_id", "services", ["environment_id"])


def downgrade() -> None:
    op.drop_index("ix_services_environment_id", table_name="services")
