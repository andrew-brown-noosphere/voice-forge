#!/usr/bin/env python
"""
Script to manually add a marketing chunk and test the content generation.
"""
import sys
import os
import logging
import uuid
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.session import get_db_session
from database.models import Content, ContentChunk
from processor.rag_service import RAGService
from database.db import Database

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Marketing content for testing
MARKETING_CONTENT = """
Product Marketing Strategy, Simplified

Create compelling positioning, messaging, and go-to-market strategies in minutes, not months.

Strategic Positioning
Create compelling positioning that differentiates your products in crowded markets

Persona Development
Build detailed buyer personas that help target your most valuable customers

Messaging Framework
Craft consistent messaging that resonates with your target audience

Trusted by Marketing Teams
"voyant.io has transformed how we approach product marketing. What used to take weeks now takes hours." 
Jamie Davis, Director of Marketing, TechCorp

"Our messaging is now consistent across all channels, and our quarterly planning process is seamless."
Alex Liu, PMM Lead, GrowthStart

"The AI assistant helped us refine our positioning in ways we hadn't considered. Game changer!"
Sarah Reynolds, VP Marketing, CloudSolutions

Everything You Need for Product Marketing Success

AI-Powered Strategy Development
Generate positioning statements with a few clicks
Create custom messaging for different audience segments
Plan quarterly GTM activities with intelligent suggestions
Analyze competitors and identify unique advantages

Collaborative Workspace
Share projects with your entire marketing team
Get feedback and iterate on strategies in real-time
Export beautifully formatted documents for stakeholders
Track changes and version history for all content

Ready to transform your product marketing?
Join thousands of product marketers using voyant.io to create winning strategies.
No credit card required • Free plan available
"""

def add_marketing_chunk():
    """Add a marketing chunk directly to the database."""
    try:
        # Get a session
        session = get_db_session()
        if hasattr(session, "__next__"):
            session = next(session)
        
        # Generate IDs
        content_id = str(uuid.uuid4())
        chunk_id = str(uuid.uuid4())
        
        # First check if we already have content in the database
        content_count = session.query(Content).count()
        logger.info(f"Found {content_count} content items in the database")
        
        # Create a content entry if needed
        if content_count == 0:
            logger.info("Creating a new content entry")
            content = Content(
                id=content_id,
                url="https://pmm.voyant.io",
                domain="pmm.voyant.io",
                text=MARKETING_CONTENT,
                html=f"<div>{MARKETING_CONTENT}</div>",
                crawl_id="manual_crawl",
                extracted_at=datetime.utcnow(),
                title="Product Marketing Strategy, Simplified",
                author="Voyant",
                publication_date=datetime.utcnow(),
                last_modified=datetime.utcnow(),
                categories=["marketing", "product"],
                tags=["marketing", "product marketing", "strategy"],
                language="en",
                content_type="landing_page"
            )
            session.add(content)
            session.commit()
            logger.info(f"Created content with ID: {content_id}")
        else:
            # Use an existing content ID
            logger.info("Using existing content")
            content = session.query(Content).first()
            content_id = content.id
        
        # Check if we already have chunks
        chunk_count = session.query(ContentChunk).count()
        logger.info(f"Found {chunk_count} chunks in the database")
        
        # Create a chunk for "marketing" if needed
        if chunk_count == 0:
            logger.info("Creating a marketing chunk")
            marketing_text = """Product Marketing Strategy, Simplified. Create compelling positioning, messaging, and go-to-market strategies in minutes, not months. Strategic Positioning, Persona Development, Messaging Framework. Everything You Need for Product Marketing Success."""
            
            # Create a chunk record
            chunk = ContentChunk(
                id=chunk_id,
                content_id=content_id,
                chunk_index=0,
                text=marketing_text,
                start_char=0,
                end_char=len(marketing_text),
                embedding=None,  # We don't need embeddings for simple text search
                chunk_metadata={
                    "title": "Product Marketing Strategy",
                    "content_type": "landing_page",
                    "domain": "pmm.voyant.io",
                    "url": "https://pmm.voyant.io",
                    "created_at": datetime.utcnow().isoformat()
                }
            )
            session.add(chunk)
            session.commit()
            logger.info(f"Created marketing chunk with ID: {chunk_id}")
        
        # Add simple text search method to the Database class if it doesn't exist
        if not hasattr(Database, 'search_chunks_by_text'):
            logger.info("Adding text search method to Database class")
            
            # Define the method that will be added
            def search_chunks_by_text(self, query, top_k=5, domain=None, content_type=None):
                """
                Search for chunks by text content.
                This is a simple fallback when vector search doesn't work.
                """
                try:
                    # Build query with filters
                    query_obj = session.query(ContentChunk)
                    
                    # Join with Content for domain/type filtering
                    if domain or content_type:
                        query_obj = query_obj.join(Content, ContentChunk.content_id == Content.id)
                        
                        if domain:
                            query_obj = query_obj.filter(Content.domain == domain)
                        
                        if content_type:
                            query_obj = query_obj.filter(Content.content_type == content_type)
                    
                    # Get all matching chunks (we'll do text matching in Python)
                    all_chunks = query_obj.all()
                    
                    # Filter and score chunks by text match
                    matching_chunks = []
                    for chunk in all_chunks:
                        # Simple text search - check if query terms are in the chunk
                        query_terms = query.lower().split()
                        chunk_text = chunk.text.lower()
                        
                        # Count matches
                        match_count = 0
                        for term in query_terms:
                            if term in chunk_text:
                                match_count += 1
                        
                        # Calculate score based on match percentage
                        if match_count > 0:
                            score = match_count / len(query_terms)
                            
                            # Add to results with score
                            matching_chunks.append({
                                "id": chunk.id,
                                "content_id": chunk.content_id,
                                "chunk_index": chunk.chunk_index,
                                "text": chunk.text,
                                "start_char": chunk.start_char,
                                "end_char": chunk.end_char,
                                "metadata": chunk.chunk_metadata,
                                "similarity": score
                            })
                    
                    # Sort by score and limit results
                    matching_chunks.sort(key=lambda x: x["similarity"], reverse=True)
                    return matching_chunks[:top_k]
                    
                except Exception as e:
                    logger.error(f"Error in text search: {str(e)}")
                    return []
            
            # Add the method to the Database class
            from types import MethodType
            Database.search_chunks_by_text = search_chunks_by_text
            logger.info("Added search_chunks_by_text method to Database class")
        
        logger.info("Successfully set up the database for marketing queries")
        return True
    
    except Exception as e:
        logger.error(f"Error setting up database: {str(e)}")
        return False
    finally:
        if 'session' in locals():
            session.close()

def test_rag_query(query="marketing"):
    """Test the RAG query with the given search term."""
    try:
        # Get a fresh session
        session = get_db_session()
        if hasattr(session, "__next__"):
            session = next(session)
        
        db = Database(session)
        
        # Add the text search method if needed
        if not hasattr(db, 'search_chunks_by_text'):
            logger.info("Adding text search method to db instance")
            
            def search_chunks_by_text(self, query, top_k=5, domain=None, content_type=None):
                """Simple text search implementation."""
                try:
                    from sqlalchemy import or_
                    
                    # Build query with filters
                    query_obj = self.session.query(ContentChunk)
                    
                    # Join with Content for domain/type filtering
                    if domain or content_type:
                        query_obj = query_obj.join(Content, ContentChunk.content_id == Content.id)
                        
                        if domain:
                            query_obj = query_obj.filter(Content.domain == domain)
                        
                        if content_type:
                            query_obj = query_obj.filter(Content.content_type == content_type)
                    
                    # Create text search conditions
                    conditions = []
                    for term in query.lower().split():
                        if term:
                            # Use LIKE for case-insensitive matching
                            conditions.append(ContentChunk.text.ilike(f'%{term}%'))
                    
                    if conditions:
                        query_obj = query_obj.filter(or_(*conditions))
                    
                    # Limit results
                    chunks = query_obj.limit(top_k).all()
                    
                    # Convert to dictionaries with similarity scores
                    results = []
                    for chunk in chunks:
                        # Calculate a simple score
                        score = 0.5  # Default score
                        
                        # Create result dictionary
                        results.append({
                            "id": chunk.id,
                            "content_id": chunk.content_id,
                            "chunk_index": chunk.chunk_index,
                            "text": chunk.text,
                            "start_char": chunk.start_char,
                            "end_char": chunk.end_char,
                            "metadata": chunk.chunk_metadata,
                            "similarity": score
                        })
                    
                    return results
                
                except Exception as e:
                    logger.error(f"Error in text search: {str(e)}")
                    return []
            
            # Add the method to the db instance
            from types import MethodType
            db.search_chunks_by_text = MethodType(search_chunks_by_text, db)
        
        # Create a RAG service
        rag_service = RAGService(db)
        
        # Test the search directly
        logger.info(f"Testing search for '{query}'")
        chunks = db.search_chunks_by_text(query=query, top_k=5)
        
        if chunks:
            logger.info(f"Found {len(chunks)} chunks containing '{query}'")
            for i, chunk in enumerate(chunks):
                logger.info(f"Chunk {i+1}: {chunk['text'][:100]}...")
        else:
            logger.warning(f"No chunks found for '{query}'")
        
        # Test the RAG system directly without going through the high-level API
        logger.info(f"Testing RAG system directly for '{query}'")
        chunks = rag_service.rag_system.retrieve_relevant_chunks(
            query=query,
            top_k=5
        )
        
        if chunks:
            logger.info(f"RAG system found {len(chunks)} chunks for '{query}'")
            # Generate a response directly using the RAG system
            response = rag_service.rag_system.generate_template_response(
                query=query,
                platform="website",
                tone="professional",
                chunks=chunks
            )
            
            logger.info(f"Generated response: {response['text']}")
            return response
        else:
            logger.warning(f"RAG system found no chunks for '{query}'")
            return None
        
    except Exception as e:
        logger.error(f"Error testing RAG query: {str(e)}")
        return None
    finally:
        if 'session' in locals():
            session.close()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Add marketing chunk and test RAG")
    parser.add_argument("--query", default="marketing", help="Query to test")
    parser.add_argument("--test-only", action="store_true", help="Skip adding chunk, just test")
    
    args = parser.parse_args()
    
    if not args.test_only:
        logger.info("Adding marketing chunk to database")
        add_marketing_chunk()
    
    logger.info(f"Testing RAG with query: {args.query}")
    test_rag_query(args.query)
