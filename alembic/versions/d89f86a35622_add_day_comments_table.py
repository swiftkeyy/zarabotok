"""add_day_comments_table

Revision ID: d89f86a35622
Revises: 4b5c3818a1cb
Create Date: 2026-04-24 10:25:57.168425

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd89f86a35622'
down_revision: Union[str, None] = '4b5c3818a1cb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create day_comments table for storing text notes on calendar days."""
    
    op.create_table(
        'day_comments',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('comment', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'date', name='uq_user_date_comment'),
        sa.CheckConstraint('LENGTH(comment) <= 500', name='ck_comment_length')
    )
    
    # Create indexes for faster lookups
    op.create_index('ix_day_comments_user_id', 'day_comments', ['user_id'])
    op.create_index('ix_day_comments_user_date', 'day_comments', ['user_id', 'date'])


def downgrade() -> None:
    """Drop day_comments table."""
    
    op.drop_index('ix_day_comments_user_date', table_name='day_comments')
    op.drop_index('ix_day_comments_user_id', table_name='day_comments')
    op.drop_table('day_comments')
