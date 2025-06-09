"""Add abstracted signal tracking system

Revision ID: 004
Revises: 003_pinecone_integration
Create Date: 2025-06-04 15:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, ARRAY


# revision identifiers, used by Alembic.
revision = '004'
down_revision = '003_pinecone_integration'
branch_labels = None
depends_on = None


def upgrade():
    """Add abstracted signal tracking system with support for multiple platforms"""
    
    # Create signals table (abstracted for all platforms)
    op.create_table(
        'signals',
        sa.Column('signal_id', sa.String(), nullable=False),
        sa.Column('org_id', sa.String(), nullable=False),
        sa.Column('platform', sa.String(), nullable=False),  # 'reddit', 'twitter', 'github', 'linkedin'
        sa.Column('platform_id', sa.String(), nullable=False),  # platform-specific ID (post_id, tweet_id, etc)
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('url', sa.String(), nullable=False),
        sa.Column('author', sa.String(), nullable=True),
        sa.Column('author_url', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),  # when content was created on platform
        sa.Column('discovered_at', sa.DateTime(), nullable=False),  # when we discovered it
        sa.Column('signal_type', sa.String(), nullable=False),  # 'question', 'complaint', 'feature_request', etc.
        sa.Column('relevance_score', sa.Float(), nullable=False),
        sa.Column('engagement_potential', sa.Float(), nullable=False),
        sa.Column('sentiment_score', sa.Float(), nullable=True),
        sa.Column('status', sa.String(), nullable=False, default='active'),  # 'active', 'archived', 'responded'
        sa.Column('platform_metadata', JSONB(), nullable=True),  # platform-specific data
        sa.Column('keywords_matched', ARRAY(sa.String()), nullable=True),
        sa.Column('engagement_metrics', JSONB(), nullable=True),  # likes, shares, comments, etc.
        sa.PrimaryKeyConstraint('signal_id'),
    )
    
    # Create indexes for signals
    op.create_index('ix_signals_org_id', 'signals', ['org_id'])
    op.create_index('ix_signals_platform', 'signals', ['platform'])
    op.create_index('ix_signals_org_platform', 'signals', ['org_id', 'platform'])
    op.create_index('ix_signals_signal_type', 'signals', ['signal_type'])
    op.create_index('ix_signals_org_signal_type', 'signals', ['org_id', 'signal_type'])
    op.create_index('ix_signals_relevance_score', 'signals', ['relevance_score'])
    op.create_index('ix_signals_discovered_at', 'signals', ['discovered_at'])
    op.create_index('ix_signals_platform_id', 'signals', ['platform', 'platform_id'])
    op.create_index('ix_signals_status', 'signals', ['status'])
    
    # Create signal_sources table to track monitoring configurations
    op.create_table(
        'signal_sources',
        sa.Column('source_id', sa.String(), nullable=False),
        sa.Column('org_id', sa.String(), nullable=False),
        sa.Column('platform', sa.String(), nullable=False),
        sa.Column('source_name', sa.String(), nullable=False),  # subreddit name, hashtag, repo, etc.
        sa.Column('source_type', sa.String(), nullable=False),  # 'subreddit', 'hashtag', 'repository', 'company_page'
        sa.Column('keywords', ARRAY(sa.String()), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('last_crawled_at', sa.DateTime(), nullable=True),
        sa.Column('crawl_frequency', sa.String(), nullable=False, default='daily'),  # 'hourly', 'daily', 'weekly'
        sa.Column('relevance_threshold', sa.Float(), nullable=False, default=0.6),
        sa.Column('config', JSONB(), nullable=True),  # platform-specific configuration
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('source_id'),
    )
    
    # Create indexes for signal_sources
    op.create_index('ix_signal_sources_org_id', 'signal_sources', ['org_id'])
    op.create_index('ix_signal_sources_platform', 'signal_sources', ['platform'])
    op.create_index('ix_signal_sources_org_platform', 'signal_sources', ['org_id', 'platform'])
    op.create_index('ix_signal_sources_is_active', 'signal_sources', ['is_active'])
    
    # Create signal_responses table
    op.create_table(
        'signal_responses',
        sa.Column('response_id', sa.String(), nullable=False),
        sa.Column('signal_id', sa.String(), sa.ForeignKey('signals.signal_id'), nullable=False),
        sa.Column('org_id', sa.String(), nullable=False),
        sa.Column('generated_content', sa.Text(), nullable=False),
        sa.Column('response_type', sa.String(), nullable=False),  # 'comment_reply', 'thread_start', 'dm', 'quote_tweet'
        sa.Column('platform', sa.String(), nullable=False),
        sa.Column('tone', sa.String(), nullable=False),
        sa.Column('confidence_score', sa.Float(), nullable=False),
        sa.Column('response_metadata', JSONB(), nullable=True),
        sa.Column('generated_at', sa.DateTime(), nullable=False),
        sa.Column('status', sa.String(), nullable=False, default='generated'),  # 'generated', 'published', 'failed'
        sa.Column('published_at', sa.DateTime(), nullable=True),
        sa.Column('platform_response_id', sa.String(), nullable=True),  # ID from platform after posting
        sa.Column('engagement_metrics', JSONB(), nullable=True),
        sa.PrimaryKeyConstraint('response_id'),
    )
    
    # Create indexes for signal_responses
    op.create_index('ix_signal_responses_org_id', 'signal_responses', ['org_id'])
    op.create_index('ix_signal_responses_signal_id', 'signal_responses', ['signal_id'])
    op.create_index('ix_signal_responses_generated_at', 'signal_responses', ['generated_at'])
    op.create_index('ix_signal_responses_confidence_score', 'signal_responses', ['confidence_score'])
    op.create_index('ix_signal_responses_status', 'signal_responses', ['status'])


def downgrade():
    """Remove signal tracking system"""
    op.drop_table('signal_responses')
    op.drop_table('signal_sources')
    op.drop_table('signals')
