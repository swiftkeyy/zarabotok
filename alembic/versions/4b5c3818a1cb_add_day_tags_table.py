"""add_day_tags_table

Revision ID: 4b5c3818a1cb
Revises: 43ffff08dc15
Create Date: 2026-04-24 10:22:03.605349

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4b5c3818a1cb'
down_revision: Union[str, None] = '43ffff08dc15'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create day_tags table for tagging calendar days with labels."""
    
    op.create_table(
        'day_tags',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('tag', sa.String(50), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'date', 'tag', name='uq_user_date_tag')
    )
    
    # Create indexes for faster lookups
    op.create_index('ix_day_tags_user_id', 'day_tags', ['user_id'])
    op.create_index('ix_day_tags_user_date', 'day_tags', ['user_id', 'date'])


def downgrade() -> None:
    """Drop day_tags table."""
    
    op.drop_index('ix_day_tags_user_date', table_name='day_tags')
    op.drop_index('ix_day_tags_user_id', table_name='day_tags')
    op.drop_table('day_tags')
