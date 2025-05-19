"""Initial database schema creation."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ARRAY, JSONB


# revision identifiers
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create extension for vector operations
    op.execute('CREATE EXTENSION IF NOT EXISTS vector;')
    
    # Create crawls table
    op.create_table(
        'crawls',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('domain', sa.String(), nullable=False),
        sa.Column('state', sa.String(), nullable=False),
        sa.Column('start_time', sa.DateTime(), nullable=True),
        sa.Column('end_time', sa.DateTime(), nullable=True),
        sa.Column('error', sa.Text(), nullable=True),
        sa.Column('config', JSONB(), nullable=False),
        sa.Column('pages_crawled', sa.Integer(), default=0),
        sa.Column('pages_discovered', sa.Integer(), default=0),
        sa.Column('pages_failed', sa.Integer(), default=0),
        sa.Column('current_depth', sa.Integer(), default=0),
        sa.Column('content_extracted', sa.Integer(), default=0),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_crawls_domain'), 'crawls', ['domain'], unique=False)
    
    # Create contents table
    op.create_table(
        'contents',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('url', sa.String(), nullable=False),
        sa.Column('domain', sa.String(), nullable=False),
        sa.Column('crawl_id', sa.String(), nullable=False),
        sa.Column('extracted_at', sa.DateTime(), nullable=False),
        sa.Column('text', sa.Text(), nullable=False),
        sa.Column('html', sa.Text(), nullable=True),
        sa.Column('title', sa.String(), nullable=True),
        sa.Column('author', sa.String(), nullable=True),
        sa.Column('publication_date', sa.DateTime(), nullable=True),
        sa.Column('last_modified', sa.DateTime(), nullable=True),
        sa.Column('categories', ARRAY(sa.String()), default=[]),
        sa.Column('tags', ARRAY(sa.String()), default=[]),
        sa.Column('language', sa.String(), nullable=True),
        sa.Column('content_type', sa.String(), nullable=False),
        sa.Column('is_processed', sa.Boolean(), default=False),
        sa.Column('entities', JSONB(), default=[]),
        sa.Column('embedding', ARRAY(sa.Float()), nullable=True),
        sa.ForeignKeyConstraint(['crawl_id'], ['crawls.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_contents_url'), 'contents', ['url'], unique=False)
    op.create_index(op.f('ix_contents_domain'), 'contents', ['domain'], unique=False)
    op.create_index(op.f('ix_contents_content_type'), 'contents', ['content_type'], unique=False)


def downgrade():
    op.drop_table('contents')
    op.drop_table('crawls')
    op.execute('DROP EXTENSION IF EXISTS vector;')
