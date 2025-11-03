"""Add passkeys table for WebAuthn credential storage.

Revision ID: 20251103_add_passkeys
Revises: 8327b05d4d00
Create Date: 2025-11-03

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '20251103_add_passkeys'
down_revision = '8327b05d4d00'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'passkeys',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('credential_id', sa.Text(), nullable=False),
        sa.Column('public_key', sa.Text(), nullable=False),
        sa.Column('counter', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.Column('name', sa.String(length=255), nullable=True),
        sa.Column('last_used_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='fk_passkeys_user_id'),
        sa.UniqueConstraint('credential_id', name='uq_passkeys_credential_id'),
    )
    op.create_index('ix_passkeys_user_id', 'passkeys', ['user_id'], unique=False)
    op.create_index('ix_passkeys_credential_id', 'passkeys', ['credential_id'], unique=True)


def downgrade() -> None:
    op.drop_index('ix_passkeys_credential_id', table_name='passkeys')
    op.drop_index('ix_passkeys_user_id', table_name='passkeys')
    op.drop_table('passkeys')

