"""add_work_orders_and_materials_tables

Revision ID: a1f23c456d78
Revises: 14a5bc355b56
Create Date: 2026-02-22 18:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'a1f23c456d78'
down_revision: Union[str, None] = '14a5bc355b56'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create work_orders table
    op.create_table(
        'work_orders',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('document_id', sa.String(36), sa.ForeignKey('documents.id', ondelete='CASCADE'), nullable=False, unique=True),
        sa.Column('linked_quotation_id', sa.String(36), sa.ForeignKey('quotations.id', ondelete='SET NULL'), nullable=True),
        sa.Column('work_order_number', sa.String(50), unique=True),
        sa.Column('client_name', sa.String(200), nullable=False),
        sa.Column('client_phone', sa.String(20)),
        sa.Column('client_email', sa.String(255)),
        sa.Column('service_location', sa.Text),
        sa.Column('work_description', sa.Text),
        sa.Column('assigned_to', sa.String(100)),
        sa.Column('start_date', sa.Date),
        sa.Column('end_date', sa.Date),
        sa.Column('labor_hours', sa.DECIMAL(6, 2)),
        sa.Column('labor_rate', sa.DECIMAL(10, 2)),
        sa.Column('labor_cost', sa.DECIMAL(12, 2)),
        sa.Column('material_cost', sa.DECIMAL(12, 2)),
        sa.Column('total_cost', sa.DECIMAL(12, 2)),
        sa.Column('status', sa.Enum('pending', 'in_progress', 'completed', 'cancelled', name='workorderstatus'), nullable=False, server_default='pending'),
        sa.Column('before_photo_url', sa.String(500)),
        sa.Column('after_photo_url', sa.String(500)),
        sa.Column('customer_signature_url', sa.String(500)),
        sa.Column('remarks', sa.Text),
        sa.Column('created_at', sa.TIMESTAMP, server_default=sa.func.now()),
        sa.Column('updated_at', sa.TIMESTAMP, server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    op.create_index('ix_work_orders_document_id', 'work_orders', ['document_id'])
    op.create_index('ix_work_orders_linked_quotation_id', 'work_orders', ['linked_quotation_id'])
    op.create_index('ix_work_orders_work_order_number', 'work_orders', ['work_order_number'])

    # Create work_order_materials table
    op.create_table(
        'work_order_materials',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('work_order_id', sa.String(36), sa.ForeignKey('work_orders.id', ondelete='CASCADE'), nullable=False),
        sa.Column('material_name', sa.String(200), nullable=False),
        sa.Column('quantity', sa.DECIMAL(10, 2)),
        sa.Column('unit', sa.String(20)),
        sa.Column('unit_cost', sa.DECIMAL(12, 2)),
        sa.Column('total_cost', sa.DECIMAL(12, 2)),
        sa.Column('order', sa.Integer),
        sa.Column('created_at', sa.TIMESTAMP, server_default=sa.func.now()),
        sa.Column('updated_at', sa.TIMESTAMP, server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    op.create_index('ix_work_order_materials_work_order_id', 'work_order_materials', ['work_order_id'])


def downgrade() -> None:
    op.drop_table('work_order_materials')
    op.drop_table('work_orders')
    op.execute("DROP TYPE IF EXISTS workorderstatus")
