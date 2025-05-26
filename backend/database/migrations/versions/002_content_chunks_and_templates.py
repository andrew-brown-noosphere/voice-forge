"""
Add content chunks and marketing templates for RAG system
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ARRAY, JSONB


# revision identifiers, used by Alembic
revision = '002_content_chunks_and_templates'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade():
    # Create content_chunks table
    op.create_table(
        'content_chunks',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('content_id', sa.String(), nullable=False),
        sa.Column('chunk_index', sa.Integer(), nullable=False),
        sa.Column('text', sa.Text(), nullable=False),
        sa.Column('start_char', sa.Integer(), nullable=False),
        sa.Column('end_char', sa.Integer(), nullable=False),
        sa.Column('embedding', sa.ARRAY(sa.Float()), nullable=True, comment='Will be converted to vector type later'),
        sa.Column('chunk_metadata', JSONB, nullable=True),
        sa.ForeignKeyConstraint(['content_id'], ['contents.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create an index for faster retrieval
    op.create_index(
        'idx_content_chunks_content_id_chunk_index',
        'content_chunks',
        ['content_id', 'chunk_index'],
        unique=False
    )
    
    # Create an index for the embeddings for vector search - TEMPORARILY DISABLED
    # op.execute(
    #     "ALTER TABLE content_chunks ALTER COLUMN embedding TYPE vector(768)"
    # )
    # op.execute(
    #     "CREATE INDEX idx_content_chunks_embedding ON content_chunks USING btree (embedding)"
    # )
    
    # Create marketing_templates table
    op.create_table(
        'marketing_templates',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('template_text', sa.Text(), nullable=False),
        sa.Column('platform', sa.String(), nullable=False),
        sa.Column('tone', sa.String(), nullable=False),
        sa.Column('purpose', sa.String(), nullable=False),
        sa.Column('parameters', JSONB, nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('created_by', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for searching templates
    op.create_index(
        'idx_marketing_templates_platform',
        'marketing_templates',
        ['platform'],
        unique=False
    )
    
    op.create_index(
        'idx_marketing_templates_tone',
        'marketing_templates',
        ['tone'],
        unique=False
    )
    
    op.create_index(
        'idx_marketing_templates_purpose',
        'marketing_templates',
        ['purpose'],
        unique=False
    )


def downgrade():
    # Drop the tables
    op.drop_table('content_chunks')
    op.drop_table('marketing_templates')
