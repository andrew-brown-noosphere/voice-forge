"""Add signal automation and AI recommendation features

Revision ID: 005
Revises: 004
Create Date: 2025-06-04 16:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, ARRAY

# revision identifiers
revision = '005'
down_revision = '004'
branch_labels = None
depends_on = None

def upgrade():
    # Add new columns to signal_sources table
    op.add_column('signal_sources', sa.Column('ai_suggested_sources', ARRAY(sa.String()), nullable=True))
    op.add_column('signal_sources', sa.Column('ai_suggested_keywords', ARRAY(sa.String()), nullable=True))
    op.add_column('signal_sources', sa.Column('business_context', sa.Text(), nullable=True))
    op.add_column('signal_sources', sa.Column('target_goals', ARRAY(sa.String()), nullable=True))
    op.add_column('signal_sources', sa.Column('performance_metrics', JSONB(), nullable=True))
    op.add_column('signal_sources', sa.Column('ai_optimization_enabled', sa.Boolean(), nullable=True, default=True))
    op.add_column('signal_sources', sa.Column('last_ai_analysis', sa.DateTime(), nullable=True))
    
    # Create signal_recommendations table
    op.create_table('signal_recommendations',
        sa.Column('recommendation_id', sa.String(), nullable=False),
        sa.Column('source_id', sa.String(), nullable=False),
        sa.Column('org_id', sa.String(), nullable=False),
        sa.Column('recommendation_type', sa.String(), nullable=False),
        sa.Column('platform', sa.String(), nullable=False),
        sa.Column('recommended_item', sa.String(), nullable=False),
        sa.Column('current_performance', JSONB(), nullable=True),
        sa.Column('predicted_improvement', JSONB(), nullable=True),
        sa.Column('confidence_score', sa.Float(), nullable=False),
        sa.Column('reasoning', sa.Text(), nullable=False),
        sa.Column('supporting_data', JSONB(), nullable=True),
        sa.Column('status', sa.String(), nullable=False, default='pending'),
        sa.Column('user_feedback', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('applied_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['source_id'], ['signal_sources.source_id'], ),
        sa.PrimaryKeyConstraint('recommendation_id')
    )
    
    # Create indexes
    op.create_index('ix_signal_recommendations_org_id', 'signal_recommendations', ['org_id'])
    op.create_index('ix_signal_recommendations_source_id', 'signal_recommendations', ['source_id'])
    op.create_index('ix_signal_recommendations_status', 'signal_recommendations', ['status'])

def downgrade():
    op.drop_table('signal_recommendations')
    op.drop_column('signal_sources', 'last_ai_analysis')
    op.drop_column('signal_sources', 'ai_optimization_enabled')
    op.drop_column('signal_sources', 'performance_metrics')
    op.drop_column('signal_sources', 'target_goals')
    op.drop_column('signal_sources', 'business_context')
    op.drop_column('signal_sources', 'ai_suggested_keywords')
    op.drop_column('signal_sources', 'ai_suggested_sources')
