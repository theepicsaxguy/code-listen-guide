"""Add missing Stripe metadata fields to payments table

Revision ID: 20251031_add_payment_metadata
Revises: 20241025_add_workflow_checkpoints
Create Date: 2025-10-31

This migration adds fields to the payments table to capture all Stripe payment
metadata that is currently missing but defined in the PaymentResponse schema.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '20251031_add_payment_metadata'
down_revision: Union[str, None] = '20241028_add_is_admin'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add Stripe metadata fields to payments table."""
    # Add stripe_customer_id
    op.add_column('payments', sa.Column('stripe_customer_id', sa.String(255), nullable=True))
    
    # Add receipt_url
    op.add_column('payments', sa.Column('receipt_url', sa.String(500), nullable=True))
    
    # Add refund_status
    op.add_column('payments', sa.Column('refund_status', sa.String(50), nullable=True))
    
    # Add refunded_amount_cents
    op.add_column('payments', sa.Column('refunded_amount_cents', sa.Integer(), nullable=True))
    
    # Add failure_code
    op.add_column('payments', sa.Column('failure_code', sa.String(100), nullable=True))
    
    # Add failure_message
    op.add_column('payments', sa.Column('failure_message', sa.Text(), nullable=True))
    
    # Add refunded_at timestamp
    op.add_column('payments', sa.Column('refunded_at', sa.DateTime(timezone=True), nullable=True))
    
    # Create index on stripe_customer_id for faster lookups
    op.create_index('ix_payments_stripe_customer_id', 'payments', ['stripe_customer_id'])


def downgrade() -> None:
    """Remove Stripe metadata fields from payments table."""
    # Drop index
    op.drop_index('ix_payments_stripe_customer_id', table_name='payments')
    
    # Drop columns
    op.drop_column('payments', 'refunded_at')
    op.drop_column('payments', 'failure_message')
    op.drop_column('payments', 'failure_code')
    op.drop_column('payments', 'refunded_amount_cents')
    op.drop_column('payments', 'refund_status')
    op.drop_column('payments', 'receipt_url')
    op.drop_column('payments', 'stripe_customer_id')
