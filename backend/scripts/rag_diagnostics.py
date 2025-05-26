#!/usr/bin/env python
"""
Diagnostic tool for the RAG system.
This script checks the health of the RAG system and identifies issues.
"""
import sys
import os
import json
import logging
import argparse
from datetime import datetime
from sqlalchemy.orm import Session

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.session import get_db_session
from database.models import Content, ContentChunk
from processor.rag_service import RAGService
from processor.rag import RAGSystem
from database.db import Database

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

def run_diagnostics():
    """Run diagnostics on the RAG system."""
    # Get database session
    session = next(get_db_session())
    db = Database(session)
    
    # Create a RAG service for testing
    rag_service = RAGService(db)
    
    issues_found = False
    report = {"timestamp": datetime.utcnow().isoformat(), "issues": []}
    
    try:
        # Check if we have any content
        content_count = session.query(Content).count()
        logger.info(f"Content items found: {content_count}")
        
        if content_count == 0:
            logger.warning("No content found in database. Please crawl some websites first.")
            report["issues"].append({
                "type": "no_content",
                "message": "No content found in database. Please crawl some websites first.",
                "severity": "high"
            })
            issues_found = True
        
        # Check if we have any chunks - using a fresh session
        chunk_session = next(get_db_session())
        try:
            from sqlalchemy import func
            chunk_count = chunk_session.query(func.count(ContentChunk.id)).scalar()
            logger.info(f"Content chunks found: {chunk_count}")
            
            if chunk_count == 0:
                logger.warning("No content chunks found. Content needs to be processed for RAG.")
                report["issues"].append({
                    "type": "no_chunks",
                    "message": "No content chunks found. Content needs to be processed for RAG.",
                    "severity": "high"
                })
                issues_found = True
                
                if content_count > 0:
                    logger.info("Content exists but no chunks. Suggesting to run the process_content_for_rag.py script.")
                    report["issues"].append({
                        "type": "chunks_needed",
                        "message": "Content exists but no chunks. Run the process_content_for_rag.py script.",
                        "severity": "high",
                        "resolution": "backend/scripts/process_content_for_rag.py"
                    })
        except Exception as chunk_error:
            logger.error(f"Error checking chunk count: {str(chunk_error)}")
            report["issues"].append({
                "type": "chunk_count_error",
                "message": f"Error checking chunk count: {str(chunk_error)}",
                "severity": "high"
            })
            issues_found = True
        finally:
            chunk_session.close()
        
        # Check embeddings - using another fresh session
        embedding_session = next(get_db_session())
        try:
            if chunk_count > 0:
                from sqlalchemy import func, text
                chunks_with_embeddings = embedding_session.query(func.count(ContentChunk.id)).filter(text("embedding IS NOT NULL")).scalar()
                logger.info(f"Chunks with embeddings: {chunks_with_embeddings}/{chunk_count}")
                
                if chunks_with_embeddings == 0:
                    logger.warning("No chunks have embeddings. This will cause RAG retrieval to fail.")
                    report["issues"].append({
                        "type": "no_embeddings",
                        "message": "No chunks have embeddings. This will cause RAG retrieval to fail.",
                        "severity": "high",
                        "resolution": "backend/scripts/process_content_for_rag.py"
                    })
                    issues_found = True
                elif chunks_with_embeddings < chunk_count:
                    logger.warning(f"Only {chunks_with_embeddings}/{chunk_count} chunks have embeddings.")
                    report["issues"].append({
                        "type": "partial_embeddings",
                        "message": f"Only {chunks_with_embeddings}/{chunk_count} chunks have embeddings.",
                        "severity": "medium",
                        "resolution": "backend/scripts/process_content_for_rag.py"
                    })
                    issues_found = True
        except Exception as embed_error:
            logger.error(f"Error checking embeddings: {str(embed_error)}")
            report["issues"].append({
                "type": "embedding_check_error",
                "message": f"Error checking embeddings: {str(embed_error)}",
                "severity": "high"
            })
            issues_found = True
        finally:
            embedding_session.close()
        
        # Test embedding model
        try:
            logger.info("Testing embedding model...")
            rag_system = rag_service.rag_system
            embedding_model = rag_system.get_embedding_model()
            
            test_text = "This is a test sentence for embeddings."
            embedding = embedding_model.encode(test_text)
            
            if embedding is not None and len(embedding) > 0:
                logger.info(f"Embedding model working. Vector dimension: {len(embedding)}")
            else:
                logger.warning("Embedding model returned empty embedding.")
                report["issues"].append({
                    "type": "embedding_model_issue",
                    "message": "Embedding model returned empty embedding.",
                    "severity": "high"
                })
                issues_found = True
        except Exception as e:
            logger.error(f"Error testing embedding model: {str(e)}")
            report["issues"].append({
                "type": "embedding_model_error",
                "message": f"Error testing embedding model: {str(e)}",
                "severity": "high"
            })
            issues_found = True
        
        # Test retrieval with a fresh session and service
        retrieval_session = next(get_db_session())
        retrieval_db = Database(retrieval_session)
        retrieval_rag_service = RAGService(retrieval_db)
        retrieval_rag_system = retrieval_rag_service.rag_system
        
        try:
            if content_count > 0 and chunk_count > 0 and chunks_with_embeddings > 0:
                logger.info("Testing chunk retrieval...")
                test_query = "test"
                chunks = retrieval_rag_system.retrieve_relevant_chunks(query=test_query, top_k=5)
                
                logger.info(f"Retrieved {len(chunks)} chunks for test query.")
                if len(chunks) == 0:
                    logger.warning("No chunks retrieved for test query.")
                    report["issues"].append({
                        "type": "retrieval_issue",
                        "message": "No chunks retrieved for test query.",
                        "severity": "medium"
                    })
                    issues_found = True
        except Exception as e:
            logger.error(f"Error testing chunk retrieval: {str(e)}")
            report["issues"].append({
                "type": "retrieval_error",
                "message": f"Error testing chunk retrieval: {str(e)}",
                "severity": "high"
            })
            issues_found = True
        finally:
            retrieval_session.close()
        
        # Test content generation with yet another fresh session
        generation_session = next(get_db_session())
        generation_db = Database(generation_session)
        generation_rag_service = RAGService(generation_db)
        generation_rag_system = generation_rag_service.rag_system
        
        try:
            if content_count > 0 and chunk_count > 0:
                logger.info("Testing content generation...")
                test_query = "test information"
                
                response = generation_rag_system.process_and_generate(
                    query=test_query,
                    platform="website",
                    tone="informative"
                )
                
                logger.info(f"Generated content: {response['text'][:100]}...")
                
                if "Sorry, I couldn't find relevant information" in response['text']:
                    logger.warning("Content generation returned the default 'not found' message.")
                    report["issues"].append({
                        "type": "generation_issue",
                        "message": "Content generation returned the default 'not found' message.",
                        "severity": "medium",
                        "resolution": "Make sure content is properly processed and has embeddings."
                    })
                    issues_found = True
        except Exception as e:
            logger.error(f"Error testing content generation: {str(e)}")
            report["issues"].append({
                "type": "generation_error",
                "message": f"Error testing content generation: {str(e)}",
                "severity": "high"
            })
            issues_found = True
        finally:
            generation_session.close()
        
        # Test pgvector extension with a final fresh session
        pgvector_session = next(get_db_session())
        try:
            logger.info("Testing pgvector extension...")
            from sqlalchemy.sql.expression import text
            extension_check = pgvector_session.execute(text("SELECT 1 FROM pg_extension WHERE extname = 'vector'")).fetchone()
            
            if extension_check:
                logger.info("pgvector extension is available in the database.")
            else:
                logger.warning("pgvector extension is not available in the database.")
                report["issues"].append({
                    "type": "pgvector_missing",
                    "message": "pgvector extension is not available in the database. Vector search will fall back to Python-based similarity, which is much slower.",
                    "severity": "medium"
                })
                issues_found = True
        except Exception as e:
            logger.error(f"Error checking pgvector extension: {str(e)}")
            report["issues"].append({
                "type": "pgvector_check_error",
                "message": f"Error checking pgvector extension: {str(e)}",
                "severity": "medium"
            })
        finally:
            pgvector_session.close()
        
        # Overall system status
        if not issues_found:
            logger.info("🎉 All diagnostics passed! No issues found in the RAG system.")
            report["status"] = "healthy"
        else:
            logger.warning("⚠️ Issues found in the RAG system. See the report for details.")
            report["status"] = "issues_found"
        
        # Print report
        logger.info(f"Diagnostic report: {json.dumps(report, indent=2)}")
        
        # Write report to file
        with open("rag_diagnostic_report.json", "w") as f:
            json.dump(report, f, indent=2)
        
        logger.info("Report saved to rag_diagnostic_report.json")
        
    except Exception as e:
        logger.error(f"Error running diagnostics: {str(e)}")
    finally:
        session.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Diagnostic tool for the RAG system")
    
    args = parser.parse_args()
    
    logger.info("Starting RAG system diagnostics")
    run_diagnostics()
    logger.info("Diagnostics completed")
