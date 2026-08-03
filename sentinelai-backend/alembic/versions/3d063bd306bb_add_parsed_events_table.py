"""add parsed_events table

Revision ID: 3d063bd306bb
Revises: d9e8f0a1b2c3
Create Date: 2026-07-29 12:21:15.604464
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '3d063bd306bb'
down_revision: Union[str, None] = 'd9e8f0a1b2c3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('parsed_events',
    sa.Column('raw_data', sa.Text(), nullable=True),
    sa.Column('event_type', sa.Text(), nullable=True),
    sa.Column('source', sa.Text(), nullable=True),
    sa.Column('severity', sa.Text(), nullable=True),
    sa.Column('id', sa.UUID(as_uuid=False), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.String(length=255), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_parsed_events_id'), 'parsed_events', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_parsed_events_id'), table_name='parsed_events')
    op.drop_table('parsed_events')
