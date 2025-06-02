"""
Add full-text search index for hybrid RAG implementation

Create Date: 2025-05-30
"""

from alembic import op
import sqlalchemy as sa


def upgrade() -> None:
    """Create PostgreSQL full-text search index for content chunks."""
    # Create full-text search index on content_chunks.content
    op.execute("""
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_content_chunks_fts 
        ON content_chunks USING GIN (to_tsvector('english', content));
    """)
    
    # Optional: Create additional indexes for better query performance
    op.execute("""
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_content_chunks_org_content_type
        ON content_chunks (org_id, content_id);
    """)


def downgrade() -> None:
    """Remove full-text search indexes."""
    op.execute("DROP INDEX IF EXISTS idx_content_chunks_fts;")
    op.execute("DROP INDEX IF EXISTS idx_content_chunks_org_content_type;")
