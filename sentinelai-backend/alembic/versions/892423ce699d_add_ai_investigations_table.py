"""add_ai_investigations_table

Revision ID: 892423ce699d
Revises: ff715ffd0bd0
Create Date: 2026-07-29 14:26:40.415640
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '892423ce699d'
down_revision: Union[str, None] = 'ff715ffd0bd0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('ai_investigations',
    sa.Column('incident_id', sa.String(length=36), nullable=False),
    sa.Column('provider', sa.String(length=50), nullable=False),
    sa.Column('prompt', sa.Text(), nullable=False),
    sa.Column('response', sa.Text(), nullable=True),
    sa.Column('summary', sa.Text(), nullable=True),
    sa.Column('attack_explanation', sa.Text(), nullable=True),
    sa.Column('timeline_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('root_cause', sa.Text(), nullable=True),
    sa.Column('mitre_explanation', sa.Text(), nullable=True),
    sa.Column('ioc_summary', sa.Text(), nullable=True),
    sa.Column('risk_explanation', sa.Text(), nullable=True),
    sa.Column('recommendations', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('containment', sa.Text(), nullable=True),
    sa.Column('recovery', sa.Text(), nullable=True),
    sa.Column('hunting_queries', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('false_positive_probability', sa.Float(), nullable=True),
    sa.Column('confidence_score', sa.Float(), nullable=True),
    sa.Column('tokens_used', sa.Integer(), nullable=True),
    sa.Column('latency_ms', sa.Integer(), nullable=True),
    sa.Column('error', sa.Text(), nullable=True),
    sa.Column('id', sa.UUID(as_uuid=False), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.String(length=255), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.ForeignKeyConstraint(['incident_id'], ['incidents.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ai_investigations_id'), 'ai_investigations', ['id'], unique=False)
    op.create_index(op.f('ix_ai_investigations_incident_id'), 'ai_investigations', ['incident_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_ai_investigations_incident_id'), table_name='ai_investigations')
    op.drop_index(op.f('ix_ai_investigations_id'), table_name='ai_investigations')
    op.drop_table('ai_investigations')
