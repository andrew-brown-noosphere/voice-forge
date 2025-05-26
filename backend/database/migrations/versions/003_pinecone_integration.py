"""
Add pinecone_id field to content_chunks table
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ARRAY, JSONB


# revision identifiers, used by Alembic
revision = '003_pinecone_integration'
down_revision = '002_content_chunks_and_templates'
branch_labels = None
depends_on = None


def upgrade():
    # Add pinecone_id field to content_chunks table
    op.add_column('content_chunks', sa.Column('pinecone_id', sa.String(), nullable=True))
    op.add_column('content_chunks', sa.Column('vector_store', sa.String(), nullable=True))
    
    # Add an index on pinecone_id
    op.create_index('idx_content_chunks_pinecone_id', 'content_chunks', ['pinecone_id'], unique=False)


def downgrade():
    # Remove pinecone_id field from content_chunks table
    op.drop_index('idx_content_chunks_pinecone_id', table_name='content_chunks')
    op.drop_column('content_chunks', 'pinecone_id')
    op.drop_column('content_chunks', 'vector_store')
