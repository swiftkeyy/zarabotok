"""add_leaderboard_tables

Revision ID: 50d1f2a12137
Revises: d89f86a35622
Create Date: 2026-04-24 10:28:50.222246

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '50d1f2a12137'
down_revision: Union[str, None] = 'd89f86a35622'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create leaderboard tables for anonymous user rankings."""
    
    # Create leaderboard_participants table
    op.create_table(
        'leaderboard_participants',
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('anonymous_id', sa.String(20), nullable=False),
        sa.Column('opted_in', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('user_id'),
        sa.UniqueConstraint('anonymous_id', name='uq_anonymous_id')
    )
    
    # Create leaderboard_scores table
    op.create_table(
        'leaderboard_scores',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('period_type', sa.String(20), nullable=False),
        sa.Column('period_key', sa.String(20), nullable=False),
        sa.Column('earnings', sa.Integer(), nullable=False),
        sa.Column('work_days', sa.Integer(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'period_type', 'period_key', name='uq_user_period')
    )
    
    # Create indexes for faster lookups
    op.create_index('ix_leaderboard_scores_period', 'leaderboard_scores', ['period_type', 'period_key'])
    op.create_index('ix_leaderboard_scores_user_id', 'leaderboard_scores', ['user_id'])


def downgrade() -> None:
    """Drop leaderboard tables."""
    
    op.drop_index('ix_leaderboard_scores_user_id', table_name='leaderboard_scores')
    op.drop_index('ix_leaderboard_scores_period', table_name='leaderboard_scores')
    op.drop_table('leaderboard_scores')
    op.drop_table('leaderboard_participants')
