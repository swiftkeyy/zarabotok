"""add_goals_table

Revision ID: 43ffff08dc15
Revises: 857954c0ffeb
Create Date: 2026-04-24 10:17:51.389033

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '43ffff08dc15'
down_revision: Union[str, None] = '857954c0ffeb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create goals table for tracking user earnings goals."""
    
    op.create_table(
        'goals',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('goal_type', sa.String(20), nullable=False),
        sa.Column('amount', sa.Integer(), nullable=False),
        sa.Column('enabled', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'goal_type', name='uq_user_goal_type')
    )
    
    # Create index for faster lookups by user_id
    op.create_index('ix_goals_user_id', 'goals', ['user_id'])


def downgrade() -> None:
    """Drop goals table."""
    
    op.drop_index('ix_goals_user_id', table_name='goals')
    op.drop_table('goals')
