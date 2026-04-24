"""add_collaborative_goals_tables

Revision ID: cf9f099673d9
Revises: 50d1f2a12137
Create Date: 2026-04-24 10:32:54.486894

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cf9f099673d9'
down_revision: Union[str, None] = '50d1f2a12137'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create collaborative goals tables for team/family shared goals."""
    
    # Create collaborative_goals table
    op.create_table(
        'collaborative_goals',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('invite_code', sa.String(10), nullable=False),
        sa.Column('goal_name', sa.String(100), nullable=False),
        sa.Column('target_amount', sa.Integer(), nullable=False),
        sa.Column('period_type', sa.String(20), nullable=False),
        sa.Column('period_key', sa.String(20), nullable=False),
        sa.Column('created_by', sa.BigInteger(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('invite_code', name='uq_invite_code')
    )
    
    # Create collaborative_goal_participants table
    op.create_table(
        'collaborative_goal_participants',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('goal_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('joined_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['goal_id'], ['collaborative_goals.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('goal_id', 'user_id', name='uq_goal_user')
    )
    
    # Create collaborative_goal_contributions table
    op.create_table(
        'collaborative_goal_contributions',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('goal_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('amount', sa.Integer(), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['goal_id'], ['collaborative_goals.id'], ondelete='CASCADE')
    )
    
    # Create indexes for faster lookups
    op.create_index('ix_collab_goals_invite_code', 'collaborative_goals', ['invite_code'])
    op.create_index('ix_collab_participants_goal_id', 'collaborative_goal_participants', ['goal_id'])
    op.create_index('ix_collab_participants_user_id', 'collaborative_goal_participants', ['user_id'])
    op.create_index('ix_collab_contributions_goal_id', 'collaborative_goal_contributions', ['goal_id'])
    op.create_index('ix_collab_contributions_user_id', 'collaborative_goal_contributions', ['user_id'])


def downgrade() -> None:
    """Drop collaborative goals tables."""
    
    op.drop_index('ix_collab_contributions_user_id', table_name='collaborative_goal_contributions')
    op.drop_index('ix_collab_contributions_goal_id', table_name='collaborative_goal_contributions')
    op.drop_index('ix_collab_participants_user_id', table_name='collaborative_goal_participants')
    op.drop_index('ix_collab_participants_goal_id', table_name='collaborative_goal_participants')
    op.drop_index('ix_collab_goals_invite_code', table_name='collaborative_goals')
    op.drop_table('collaborative_goal_contributions')
    op.drop_table('collaborative_goal_participants')
    op.drop_table('collaborative_goals')
