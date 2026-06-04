"""Widen company_logo_url for base64 logos

Revision ID: a1b2c3d4e5f6
Revises: c3477e7af3ea
Create Date: 2026-06-04

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, None] = "c3477e7af3ea"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    dialect = bind.dialect.name

    if dialect == "mysql":
        op.execute(
            "ALTER TABLE users MODIFY company_logo_url LONGTEXT NULL"
        )
    elif dialect == "postgresql":
        op.alter_column(
            "users",
            "company_logo_url",
            existing_type=sa.String(length=500),
            type_=sa.Text(),
            existing_nullable=True,
        )
    else:
        op.alter_column(
            "users",
            "company_logo_url",
            existing_type=sa.String(length=500),
            type_=sa.Text(),
            existing_nullable=True,
        )


def downgrade() -> None:
    bind = op.get_bind()
    dialect = bind.dialect.name

    if dialect == "mysql":
        op.execute(
            "ALTER TABLE users MODIFY company_logo_url VARCHAR(500) NULL"
        )
    else:
        op.alter_column(
            "users",
            "company_logo_url",
            existing_type=sa.Text(),
            type_=sa.String(length=500),
            existing_nullable=True,
        )
