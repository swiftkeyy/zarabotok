"""add_referral_system_tables

Revision ID: 785da99533dd
Revises: cf9f099673d9
Create Date: 2026-04-24 10:37:49.488401

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '785da99533dd'
down_revision: Union[str, None] = 'cf9f099673d9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create referral system tables for user invitations and bonuses."""
    
    # Create referral_codes table
    op.create_table(
        'referral_codes',
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('code', sa.String(10), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('user_id'),
        sa.UniqueConstraint('code', name='uq_referral_code')
    )
    
    # Create referrals table
    op.create_table(
        'referrals',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('referrer_id', sa.BigInteger(), nullable=False),
        sa.Column('referred_id', sa.BigInteger(), nullable=False),
        sa.Column('referral_code', sa.String(10), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('bonus_awarded', sa.Boolean(), nullable=False, server_default=sa.text('FALSE')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('referred_id', name='uq_referred_user')
    )
    
    # Create indexes for faster lookups
    op.create_index('ix_referral_codes_code', 'referral_codes', ['code'])
    op.create_index('ix_referrals_referrer_id', 'referrals', ['referrer_id'])
    op.create_index('ix_referrals_referred_id', 'referrals', ['referred_id'])
    op.create_index('ix_referrals_code', 'referrals', ['referral_code'])


def downgrade() -> None:
    """Drop referral system tables."""
    
    op.drop_index('ix_referrals_code', table_name='referrals')
    op.drop_index('ix_referrals_referred_id', table_name='referrals')
    op.drop_index('ix_referrals_referrer_id', table_name='referrals')
    op.drop_index('ix_referral_codes_code', table_name='referral_codes')
    op.drop_table('referrals')
    op.drop_table('referral_codes')
