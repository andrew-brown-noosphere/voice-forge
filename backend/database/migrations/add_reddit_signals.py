"""
Add Reddit signal models to database

Revision ID: add_reddit_signals
Create Date: 2025-06-04
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, ARRAY


def upgrade():
    """Add Reddit signal tracking tables"""
    
    # Create reddit_signals table
    op.create_table(
        'reddit_signals',
        sa.Column('signal_id', sa.String(), nullable=False),
        sa.Column('org_id', sa.String(), nullable=False),
        sa.Column('platform', sa.String(), nullable=False, default='reddit'),
        sa.Column('thread_id', sa.String(), nullable=False),
        sa.Column('subreddit', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('url', sa.String(), nullable=False),
        sa.Column('author', sa.String(), nullable=True),
        sa.Column('score', sa.Integer(), nullable=False, default=0),
        sa.Column('num_comments', sa.Integer(), nullable=False, default=0),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('relevance_score', sa.Float(), nullable=False),
        sa.Column('signal_type', sa.String(), nullable=False),
        sa.Column('engagement_potential', sa.Float(), nullable=False),
        sa.Column('top_comments', ARRAY(sa.Text()), nullable=True),
        sa.Column('discovered_at', sa.DateTime(), nullable=False),
        sa.Column('status', sa.String(), nullable=False, default='active'),
        sa.Column('signal_metadata', JSONB(), nullable=True),
        sa.PrimaryKeyConstraint('signal_id'),
    )
    
    # Create indexes for reddit_signals
    op.create_index('ix_reddit_signals_org_id', 'reddit_signals', ['org_id'])
    op.create_index('ix_reddit_signals_org_id_subreddit', 'reddit_signals', ['org_id', 'subreddit'])
    op.create_index('ix_reddit_signals_org_id_signal_type', 'reddit_signals', ['org_id', 'signal_type'])
    op.create_index('ix_reddit_signals_relevance_score', 'reddit_signals', ['relevance_score'])
    op.create_index('ix_reddit_signals_discovered_at', 'reddit_signals', ['discovered_at'])
    op.create_index('ix_reddit_signals_thread_id', 'reddit_signals', ['thread_id'])
    
    # Create signal_responses table
    op.create_table(
        'signal_responses',
        sa.Column('response_id', sa.String(), nullable=False),
        sa.Column('signal_id', sa.String(), sa.ForeignKey('reddit_signals.signal_id'), nullable=False),
        sa.Column('org_id', sa.String(), nullable=False),
        sa.Column('generated_content', sa.Text(), nullable=False),
        sa.Column('response_type', sa.String(), nullable=False),
        sa.Column('platform', sa.String(), nullable=False),
        sa.Column('tone', sa.String(), nullable=False),
        sa.Column('confidence_score', sa.Float(), nullable=False),
        sa.Column('response_metadata', JSONB(), nullable=True),
        sa.Column('generated_at', sa.DateTime(), nullable=False),
        sa.Column('status', sa.String(), nullable=False, default='generated'),
        sa.Column('published_at', sa.DateTime(), nullable=True),
        sa.Column('engagement_metrics', JSONB(), nullable=True),
        sa.PrimaryKeyConstraint('response_id'),
    )
    
    # Create indexes for signal_responses
    op.create_index('ix_signal_responses_org_id', 'signal_responses', ['org_id'])
    op.create_index('ix_signal_responses_signal_id', 'signal_responses', ['signal_id'])
    op.create_index('ix_signal_responses_generated_at', 'signal_responses', ['generated_at'])
    op.create_index('ix_signal_responses_confidence_score', 'signal_responses', ['confidence_score'])


def downgrade():
    """Remove Reddit signal tracking tables"""
    op.drop_table('signal_responses')
    op.drop_table('reddit_signals')
