"""
Retrieval-Augmented Generation (RAG) system for VoiceForge with enhanced retrieval.
"""
import logging
import uuid
import os
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import re
import json
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import time

from processor.chunker import ContentChunker
from processor.pinecone_rag import PineconeRAGStore
from processor.retrieval.relevance_scoring import RelevanceScorer
from processor.retrieval.context_filter import ContextFilter
from processor.retrieval.hybrid_retriever import HybridRetriever
from processor.retrieval.query_reformulation import QueryReformulator

logger = logging.getLogger(__name__)

class RAGSystem:
    """
    Implementation of a Retrieval-Augmented Generation system for VoiceForge.
    Retrieves relevant content chunks and generates brand-consistent responses.
    """
    
    def __init__(self, db, embedding_model=None):
        """
        Initialize the RAG system.
        
        Args:
            db: Database interface
            embedding_model: Optional pre-initialized embedding model
        """
        self.db = db
        self.embedding_model = embedding_model
        self.chunker = ContentChunker(chunk_size=500, chunk_overlap=100)
        
        # Initialize vector store
        self.use_pinecone = os.environ.get('VECTOR_DB_PROVIDER', '').lower() == 'pinecone'
        if self.use_pinecone:
            self.vector_store = PineconeRAGStore(db)
            logger.info("Using Pinecone for RAG vector storage")
        else:
            self.vector_store = None
            logger.info("Using database for RAG vector storage")
            
        # Initialize enhanced retrieval components
        self.relevance_scorer = RelevanceScorer()
        self.context_filter = ContextFilter()
        self.query_reformulator = QueryReformulator()
        
        # Initialize hybrid retriever after embedding model is set
        self.hybrid_retriever = None
    
    def get_embedding_model(self):
        """Lazy-load the embedding model with fallbacks."""
        if self.embedding_model is None:
            # Try to get embedding model from processor service
            try:
                from processor.service import ProcessorService
                processor_service = ProcessorService(self.db)
                self.embedding_model = processor_service.get_embedding_model()
                logger.info("Using embedding model from processor service")
            except Exception as e:
                logger.error(f"Failed to get embedding model from processor service: {e}")
                
                # Try importing directly
                try:
                    from sentence_transformers import SentenceTransformer
                    self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
                    logger.info("Initialized SentenceTransformer model directly")
                except ImportError:
                    # If sentence_transformers is not available, use TF-IDF
                    logger.warning("SentenceTransformer not available, using TF-IDF embeddings")
                    from processor.service import SimpleTfIdfEmbedder
                    self.embedding_model = SimpleTfIdfEmbedder(dimension=768)
                except Exception as e:
                    logger.error(f"Failed to initialize embedding model: {e}")
                    
                    # Last resort: Create a dummy embedding model
                    logger.warning("Using random embedding model as last resort")
                    
                    class RandomEmbedder:
                        """Simple random vector generator as a last resort."""
                        def encode(self, texts, **kwargs):
                            """Generate random vectors."""
                            if isinstance(texts, str):
                                return np.random.rand(768).astype(np.float32)
                            else:
                                return np.random.rand(len(texts), 768).astype(np.float32)
                    
                    self.embedding_model = RandomEmbedder()
                    
            # Initialize hybrid retriever now that embedding model is available
            if self.hybrid_retriever is None:
                self.hybrid_retriever = HybridRetriever(self.db, self.embedding_model)
        
        return self.embedding_model
    
    def process_content_for_rag(self, content_id: str) -> bool:
        """
        Process content into chunks for RAG.
        
        Args:
            content_id: ID of the content to process
            
        Returns:
            Success status
        """
        try:
            # Get content from database
            content = self.db.get_content(content_id)
            if not content:
                logger.warning(f"Content {content_id} not found")
                return False
            
            # Split content into chunks
            chunks = self.chunker.process_content(content)
            logger.info(f"Generated {len(chunks)} chunks for content {content_id}")
            
            # Generate embeddings for chunks
            model = self.get_embedding_model()
            
            # Process chunks in batches to avoid memory issues
            batch_size = 32
            for i in range(0, len(chunks), batch_size):
                batch = chunks[i:i+batch_size]
                texts = [chunk["text"] for chunk in batch]
                
                # Generate embeddings
                embeddings = model.encode(texts)
                
                # Update chunks with embeddings
                for j, embedding in enumerate(embeddings):
                    batch[j]["embedding"] = embedding.tolist()
                
                # Store chunks in vector database or regular database
                if self.use_pinecone and self.vector_store:
                    success = self.vector_store.store_chunks(batch)
                    if not success:
                        logger.warning(f"Failed to store chunks in Pinecone, falling back to database")
                        self.db.store_content_chunks(batch)
                else:
                    # Store chunks in database
                    self.db.store_content_chunks(batch)
            
            logger.info(f"Successfully processed content {content_id} for RAG")
            return True
            
        except Exception as e:
            logger.error(f"Failed to process content {content_id} for RAG: {str(e)}")
            return False
    
    def retrieve_relevant_chunks(
        self, 
        query: str, 
        top_k: int = 5, 
        domain: Optional[str] = None,
        content_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve the most relevant chunks for a query.
        
        Args:
            query: Search query
            top_k: Number of chunks to retrieve
            domain: Optional domain filter
            content_type: Optional content type filter
            
        Returns:
            List of relevant chunks with similarity scores
        """
        start_time = time.time()
        logger.info(f"Retrieving chunks for query: {query}")
        
        # Initialize hybrid retriever if needed
        if self.hybrid_retriever is None:
            model = self.get_embedding_model()
            self.hybrid_retriever = HybridRetriever(self.db, model)
        
        # Step 1: Reformulate query for better retrieval
        reformulated_queries = self.query_reformulator.reformulate(query)
        logger.debug(f"Reformulated queries: {reformulated_queries}")
        
        # Step 2: Retrieve chunks for each reformulation
        all_chunks = []
        for reformulated_query in reformulated_queries:
            # Use hybrid retrieval (combines vector and keyword search)
            chunks = self.hybrid_retriever.retrieve(
                query=reformulated_query,
                top_k=top_k,  # Get top_k for each reformulation
                domain=domain,
                content_type=content_type
            )
            all_chunks.extend(chunks)
        
        # Step 3: Deduplicate chunks by ID
        unique_chunks = {}
        for chunk in all_chunks:
            chunk_id = chunk["id"]
            if chunk_id not in unique_chunks or chunk["similarity"] > unique_chunks[chunk_id]["similarity"]:
                unique_chunks[chunk_id] = chunk
        
        # Convert to list
        chunks = list(unique_chunks.values())
        
        # Step 4: Apply enhanced scoring
        model = self.get_embedding_model()
        query_embedding = model.encode(query).tolist()
        
        enhanced_chunks = []
        for chunk in chunks:
            final_score, score_components = self.relevance_scorer.score_chunk(
                chunk=chunk,
                query=query,
                query_embedding=query_embedding
            )
            
            # Update chunk with new score and components
            chunk["similarity"] = final_score
            chunk["score_components"] = score_components
            enhanced_chunks.append(chunk)
        
        # Step 5: Apply context-aware filtering
        filtered_chunks = self.context_filter.filter_chunks(
            chunks=enhanced_chunks,
            query=query
        )
        
        # Sort by final score and limit to top_k
        filtered_chunks.sort(key=lambda x: x["similarity"], reverse=True)
        result_chunks = filtered_chunks[:top_k]
        
        elapsed_time = time.time() - start_time
        logger.info(f"Retrieved {len(result_chunks)} chunks in {elapsed_time:.2f}s")
        
        return result_chunks
    
    def generate_ai_response(
        self, 
        query: str, 
        platform: str, 
        tone: str, 
        chunks: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate AI-powered response using OpenAI GPT.
        
        Args:
            query: Original query
            platform: Target platform (e.g., "twitter", "email")
            tone: Desired tone (e.g., "professional", "casual")
            chunks: Retrieved relevant chunks
            
        Returns:
            AI-generated response
        """
        try:
            from processor.ai_content_generator import AIContentGenerator
            
            # Initialize AI generator
            ai_generator = AIContentGenerator()
            
            # Generate AI-powered content
            response = ai_generator.generate_content(
                query=query,
                platform=platform,
                tone=tone,
                chunks=chunks
            )
            
            logger.info(f"Generated AI content for query: {query[:50]}...")
            return response
            
        except Exception as e:
            logger.error(f"Failed to generate AI response: {str(e)}")
            # Fallback to template response
            return self.generate_template_response(query, platform, tone, chunks)
    
    def generate_template_response(
        self, 
        query: str, 
        platform: str, 
        tone: str, 
        chunks: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate a response using templates as fallback.
        
        Args:
            query: Original query
            platform: Target platform (e.g., "twitter", "email")
            tone: Desired tone (e.g., "professional", "casual")
            chunks: Retrieved relevant chunks
            
        Returns:
            Template-generated response
        """
        try:
            # Extract key information from chunks
            combined_text = "\n".join([chunk["text"] for chunk in chunks])
            
            # Generate simplified context (keypoints)
            key_points = self._extract_key_points(combined_text)
            
            # Create a simple response
            response_text = f"Based on the available information about {self._extract_topic(query)}:\n\n"
            response_text += "\n".join([f"• {point}" for point in key_points[:3]])
            
            # Platform-specific adjustments
            if platform == 'twitter' and len(response_text) > 240:
                # Shorten for Twitter
                response_text = f"Key info about {self._extract_topic(query)}: {key_points[0] if key_points else combined_text[:100]}..."
            
            # Generate response metadata
            response = {
                "text": response_text,
                "source_chunks": [
                    {
                        "chunk_id": chunk["id"],
                        "text": chunk["text"][:150] + "...",
                        "similarity": chunk["similarity"],
                        "content_id": chunk["content_id"]
                    }
                    for chunk in chunks
                ],
                "metadata": {
                    "platform": platform,
                    "tone": tone,
                    "generated_at": datetime.utcnow().isoformat(),
                    "query": query,
                    "generation_method": "template_fallback"
                }
            }
            
            logger.info(f"Generated template response for query: {query[:50]}...")
            return response
            
        except Exception as e:
            logger.error(f"Failed to generate template response: {str(e)}")
            return {
                "text": f"Sorry, I couldn't generate a response at this time.",
                "error": str(e),
                "metadata": {
                    "platform": platform,
                    "tone": tone,
                    "generated_at": datetime.utcnow().isoformat(),
                    "query": query
                }
            }
    
    def _extract_topic(self, query: str) -> str:
        """Extract the main topic from a query."""
        # Simple implementation - in a production system, use NLP
        words = query.split()
        if len(words) <= 3:
            return query
        
        # Use the first few words as the topic
        return " ".join(words[:3]) + "..."
    
    def _extract_key_points(self, text: str, max_points: int = 5) -> List[str]:
        """Extract key points from text."""
        # Simple implementation - in a production system, use NLP
        sentences = re.split(r'[.!?]', text)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
        
        # Take the first few sentences as key points
        key_points = []
        for sentence in sentences[:max_points]:
            # Simplify sentences to make them more like bullet points
            simplified = re.sub(r'^(However|Moreover|Furthermore|Additionally|In addition|Also|Thus|Therefore|Hence)', '', sentence).strip()
            if simplified and len(simplified) > 15:
                key_points.append(simplified)
        
        return key_points
    
    def _fill_template(self, template: str, data: Dict[str, str]) -> str:
        """Fill a template with data."""
        result = template
        
        # Replace placeholders with data
        for key, value in data.items():
            placeholder = f"{{{{{key}}}}}"
            result = result.replace(placeholder, value)
        
        return result
    
    def process_and_generate(
        self,
        query: str,
        platform: str,
        tone: str,
        domain: Optional[str] = None,
        content_type: Optional[str] = None,
        top_k: int = 5
    ) -> Dict[str, Any]:
        """
        End-to-end process to retrieve relevant chunks and generate a response.
        
        Args:
            query: Search query
            platform: Target platform
            tone: Desired tone
            domain: Optional domain filter
            content_type: Optional content type filter
            top_k: Number of chunks to retrieve
            
        Returns:
            Generated response with source information
        """
        # Log processing request
        logger.info(f"Processing content generation request for query: {query}")
        logger.info(f"Parameters: platform={platform}, tone={tone}, domain={domain}, content_type={content_type}")
        
        # Step 1: Retrieve relevant chunks using enhanced retrieval
        chunks = self.retrieve_relevant_chunks(
            query=query,
            top_k=top_k,
            domain=domain,
            content_type=content_type
        )
        
        # Step 2: Generate response
        if not chunks:
            # No chunks found - error
            logger.warning(f"No chunks found for query: {query}")
            
            return {
                "text": f"Sorry, I couldn't find relevant information for '{query}'. Try a different query or ensure content has been processed for RAG.",
                "source_chunks": [],
                "metadata": {
                    "platform": platform,
                    "tone": tone,
                    "generated_at": datetime.utcnow().isoformat(),
                    "query": query,
                    "error": "no_relevant_chunks"
                }
            }
        
        # Generate response from chunks using AI
        response = self.generate_ai_response(
            query=query,
            platform=platform,
            tone=tone,
            chunks=chunks
        )
        
        return response
