"""initial_schema

Revision ID: 857954c0ffeb
Revises: 
Create Date: 2026-04-24 10:13:48.897623

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '857954c0ffeb'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create initial schema with users, stats, and forced_channels tables."""
    
    # Create users table
    op.create_table(
        'users',
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('username', sa.Text(), nullable=True),
        sa.Column('first_name', sa.Text(), nullable=True),
        sa.Column('joined_at', sa.DateTime(), nullable=True),
        sa.Column('last_active', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('user_id')
    )
    
    # Create stats table
    op.create_table(
        'stats',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('user_id', sa.BigInteger(), nullable=True),
        sa.Column('month', sa.Text(), nullable=True),
        sa.Column('work_days', sa.Integer(), nullable=True),
        sa.Column('earnings', sa.Integer(), nullable=True),
        sa.Column('rate', sa.Integer(), nullable=True),
        sa.Column('passive_rate', sa.Integer(), nullable=True),
        sa.Column('saved_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create forced_channels table
    op.create_table(
        'forced_channels',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('channel_id', sa.BigInteger(), nullable=True),
        sa.Column('channel_username', sa.Text(), nullable=True),
        sa.Column('title', sa.Text(), nullable=True),
        sa.Column('added_by', sa.BigInteger(), nullable=True),
        sa.Column('added_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('channel_id')
    )


def downgrade() -> None:
    """Drop all tables."""
    op.drop_table('forced_channels')
    op.drop_table('stats')
    op.drop_table('users')
