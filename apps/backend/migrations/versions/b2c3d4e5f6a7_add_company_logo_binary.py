"""Add binary company logo columns

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-06-04

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b2c3d4e5f6a7"
down_revision: Union[str, None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    dialect = bind.dialect.name

    op.add_column(
        "users",
        sa.Column("company_logo_mime", sa.String(length=64), nullable=True),
    )

    if dialect == "mysql":
        op.add_column(
            "users",
            sa.Column("company_logo_data", sa.LargeBinary(length=16777215), nullable=True),
        )
    else:
        op.add_column(
            "users",
            sa.Column("company_logo_data", sa.LargeBinary(), nullable=True),
        )


def downgrade() -> None:
    op.drop_column("users", "company_logo_data")
    op.drop_column("users", "company_logo_mime")
